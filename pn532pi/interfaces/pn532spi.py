import time

from pn532pi.interfaces.pn532Interface import Pn532Interface, PN532_ACK_WAIT_TIME, PN532_INVALID_FRAME, PN532_PN532TOHOST, \
    PN532_INVALID_ACK, PN532_TIMEOUT, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, \
    PN532_HOSTTOPN532, PN532_POSTAMBLE, REVERSE_BITS_ORDER
from spidev import SpiDev

from pn532pi.nfc.pn532_log import DMSG

STATUS_READ = 2
DATA_WRITE = 1
DATA_READ = 3

RPI_BUS0 = 0
SPI_MODE0 = 0b0


def _reverse_bits(data: bytearray) -> bytearray:
    """Reverse bit order for all bytes in a byte array"""
    return bytearray([REVERSE_BITS_ORDER(b) for b in data])


class Pn532Spi(Pn532Interface):
    SS0_GPIO8 = 0
    SS1_GPIO7 = 1

    def _get_byte(self):
        data = self._spi.readbytes(1)
        assert data, "No bytes read!"
        return REVERSE_BITS_ORDER(data[0])

    def _put_byte(self, data: int):
        self._spi.writebytes([REVERSE_BITS_ORDER(data)])

    def _send_bytes(self, data: bytearray) -> None:
        self._spi.writebytes(list(_reverse_bits(data)))

    def _receive_bytes(self, num: int) -> bytearray:
        return _reverse_bits(self._spi.readbytes(num))

    def _xfer_bytes(self, data: bytearray) -> bytearray:
        return _reverse_bits(self._spi.xfer2(list(_reverse_bits(data))))

    def _check_status(self) -> int:
        data_out = list(_reverse_bits([STATUS_READ, 0]))
        return _reverse_bits(self._spi.xfer2(data_out))[1]

    def __init__(self, ss: int, speed_hz: int=4_000_000):
        """Pass in slave select pin and optional speed (4MHz default, 5MHz max)"""
        self._command = 0
        self._ss = ss
        self._spi = SpiDev()
        assert speed_hz <= 5_000_000, "SPI Bus speed must be <= 5MHz"
        self._speed = speed_hz
        assert ss in [1, 0], 'Chip select must be 1 or 0'

    def begin(self):
        self._spi.open(RPI_BUS0, self._ss)
        self._spi.mode = SPI_MODE0  # PN532 only supports mode0
        self._spi.cshigh = False  # Active low
        self._spi.max_speed_hz = self._speed

    def wakeup(self) -> None:
        # Chip select controlled by driver
        self._isReady()

    def writeCommand(self, header: bytearray, body: bytearray = bytearray()) -> int:
        self._command = header[0]
        self._writeFrame(header, body)

        timeout = PN532_ACK_WAIT_TIME
        while (not self._isReady()):
            time.sleep(.001)    # sleep 1 ms
            timeout -= 1
            if (0 >= timeout):
                DMSG("Time out when waiting for ACK\n")
                return PN532_TIMEOUT
        if (not self._readAckFrame()):
            DMSG("Invalid ACK\n")
            return PN532_INVALID_ACK

        return 0

    def _getResponseLength(self, timeout: int):
        PN532_NACK = [0, 0, 0xFF, 0xFF, 0, 0]
        timer = 0

        while (not self._isReady()):
            time.sleep(.001)    # sleep 1 ms
            timer+=1
            if ((0 != timeout) and (timer > timeout)):
                return -1  


        data = self._xfer_bytes([DATA_READ] + [0 for i in range(5)])
        data = data[1:]  # first byte is garbage
        DMSG('_getResponseLength length frame: {!r}'.format(data))

        if data[:-2] != bytearray([PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]):
            DMSG('Invalid Response frame: {}'.format(data))
            return PN532_INVALID_FRAME

        length = data[3]
        l_checksum = data[4]
        if (0 != (length + l_checksum) & 0xFF):
            DMSG('Invalid Length Checksum: len {:d} checksum {:d}'.format(length, l_checksum))
            return PN532_INVALID_FRAME

        DMSG('_getResponseLength length is {:d}'.format(length))

        #  Not needed for SPI
        # request for last respond msg again
        # DMSG('_getResponseLength writing nack: {!r}'.format(PN532_NACK))
        # self._send_bytes([DATA_WRITE] + PN532_NACK)

        return length

    def readResponse(self, timeout: int = 1000) -> (int, bytearray):
        timer = 0
        buf = bytearray()        
        result = 0

        length = self._getResponseLength(timeout)

        if length < 0:
            return length, buf

        data = self._xfer_bytes([DATA_READ] + [0 for i in range(length + 1)])   #  Total length - 1 for RW byte, SPI is full duplex

        cmd = self._command + 1 # response command
        if (PN532_PN532TOHOST != data[0] or (cmd) != data[1]):
            return PN532_INVALID_FRAME, buf

        length -= 2

        DMSG("readResponse read command:  {:x}".format(cmd))

        dsum = PN532_PN532TOHOST + cmd
        buf = data[2:-2]
        DMSG('readResponse response: {!r}\n'.format(buf))
        dsum += sum(buf)

        checksum = data[-2]
        if (0 != (dsum + checksum) & 0xFF):
            DMSG("checksum is not ok: sum {:d} checksum {:d}\n".format(dsum, checksum))
            return PN532_INVALID_FRAME, buf
        # POSTAMBLE data [-1]

        return length, buf

    def _isReady(self) -> bool:
        status = self._check_status() & 1
        return bool(status)

    def _writeFrame(self, header: bytearray, body: bytearray):
        data_out = [DATA_WRITE, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]

        length = len(header) + len(body) + 1  # length of data field: TFI + DATA
        data_out.append(length)
        data_out.append((~length + 1) & 0xFF)

        data_out.append(PN532_HOSTTOPN532)
        dsum = PN532_HOSTTOPN532 + sum(header) + sum(body) # sum of TFI + DATA

        data_out += list(header)
        data_out += list(body)
        checksum = (~dsum + 1) & 0xFF  # checksum of TFI + DATA

        data_out += [checksum, PN532_POSTAMBLE]

        DMSG("writeCommand: {}    {}    {}".format(header, body, data_out))
        try:
            # send data
            self._send_bytes(data_out)
        except Exception as e:
            DMSG(e)
            DMSG("\nError writing frame\n")  # I2C max packet: 32 bytes
            raise

    def _readAckFrame(self):
        """Returns true if ack was successfully read"""
        PN532_ACK = bytearray([0, 0, 0xFF, 0, 0xFF, 0])

        ackBuf = self._xfer_bytes([DATA_READ] + [0 for i in range(len(PN532_ACK))])
        DMSG("_readAckFrame: ack    {}".format(ackBuf[1:]))
        return ackBuf[1:] == PN532_ACK