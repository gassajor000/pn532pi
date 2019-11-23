import binascii
import time

from PN532.pn532Interface import pn532Interface, PN532_ACK_WAIT_TIME, PN532_INVALID_FRAME, PN532_PN532TOHOST, \
    PN532_NO_SPACE, PN532_INVALID_ACK, PN532_TIMEOUT, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, \
    PN532_HOSTTOPN532, PN532_POSTAMBLE
from spidev import SpiDev

STATUS_READ = 2
DATA_WRITE = 1
DATA_READ = 3

RPI_BUS0 = 0
SPI_MODE0 = 0b0


class pn532spi(pn532Interface):
    SS0_GPIO8 = 0
    SS1_GPIO7 = 1

    def _get_byte(self):
        data = self._spi.readbytes(1)
        assert data, "No bytes read!"
        return data[0]

    def _put_byte(self, data: int):
        self._spi.writebytes([data & 0xff])

    def __init__(self, ss: int):
        self._command = 0
        self._ss = ss
        self._spi = SpiDev()
        assert ss in [1, 0], 'Chip select must be 1 or 0'

    def begin(self):
        self._spi.open(RPI_BUS0, self._ss)
        self._spi.mode = SPI_MODE0  # PN532 only supports mode0
        self._spi.lsbfirst = True
        self._spi.cshigh = False  # Active low
        self._spi.max_speed_hz = 5000000 # 5 MHz

    def wakeup(self) -> None:
        # Chip select controlled by driver
        self._spi._put_byte(0)

    def writeCommand(self, header: bytearray, body: bytearray) -> int:
        self._command = header[0]
        self._writeFrame(header, body)

        timeout = PN532_ACK_WAIT_TIME
        while (not self._isReady()):
            time.sleep(1)
            timeout -= 1
            if (0 == timeout):
                print("Time out when waiting for ACK\n")
                return -2
        if (self._readAckFrame()):
            print("Invalid ACK\n")
            return PN532_INVALID_ACK

        return 0

    def readResponse(self, timeout: int = 1000) -> (int, bytearray):
        time = 0
        while (not self._isReady()):
            time.sleep(1)
            time += 1
            if (time > timeout):
                return PN532_TIMEOUT

        result = 0
        buf = bytearray()

        while (1):
            self._spi.writebytes([DATA_READ])

            start = self._spi.readbytes(3)
            if start != [PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]:
    
                result = PN532_INVALID_FRAME
                break
    
            length = self._get_byte()
            l_checksum = self._get_byte()
            if (0 != (length + l_checksum) & 0xFF):
                result = PN532_INVALID_FRAME
                break
    
            cmd = self._command + 1 # response command
            if (PN532_PN532TOHOST != self._get_byte() or (cmd) != self._get_byte()):
                result = PN532_INVALID_FRAME
                break
    
            print("read:  {:x}".format(cmd))

            length -= 2
            if (length > len):
                for i in range(length):
                        print(self._get_byte()) # dump message
                print("\nNot enough space\n")
                self._spi.readbytes(2)
                result = PN532_NO_SPACE # not enough space
                break
    
            sum = PN532_PN532TOHOST + cmd
            data = self._spi.readbytes(length)
            buf += bytearray(data)
            sum += sum(data)

            print(data)
            print('\n')
    
            checksum = self._get_byte()
            if (0 != (sum + checksum) & 0xFf):
                print("checksum is not ok\n")
                result = PN532_INVALID_FRAME
                break
            self._get_byte() # POSTAMBLE
    
            result = length
            break

        return result, buf

    def _isReady(self) -> bool:
        self._put_byte(STATUS_READ)
        status = self._get_byte() & 1
        return bool(status)

    def _writeFrame(self, header: bytearray, body: bytearray):
        digitalWrite(self._ss, LOW)
        time.sleep(2) # wake up PN532

        write(DATA_WRITE)
        write(PN532_PREAMBLE)
        write(PN532_STARTCODE1)
        write(PN532_STARTCODE2)

        length = hlen + blen + 1 # length of data field: TFI + DATA
        write(length)
        write(~length + 1) # checksum of length

        write(PN532_HOSTTOPN532)
        sum = PN532_HOSTTOPN532 # sum of TFI + DATA

        print("write: ")

        for  i in range(hlen):
            write(header[i])
            sum += header[i]

            print('{:x}'.format(header[i]))
        for  i in range(blen):
            write(body[i])
            sum += body[i]

            print('{:x}'.format(body[i]))

        checksum = ~sum + 1 # checksum of TFI + DATA
        write(checksum)
        write(PN532_POSTAMBLE)

        digitalWrite(self._ss, HIGH)

        print('\n')

    def _readAckFrame(self):
        PN532_ACK = [0, 0, 0xFF, 0, 0xFF, 0]

        ackBuf = []

        digitalWrite(_ss, LOW)
        time.sleep(1)
        write(DATA_READ)

        for i in range(PN532_ACK):
            ackBuf[i] = read()

        digitalWrite(self._ss, HIGH)

        return ackBuf == PN532_ACK