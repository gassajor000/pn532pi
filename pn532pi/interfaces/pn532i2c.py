import time

from pn532pi.nfc.pn532_log import DMSG
from quick2wire.i2c import I2CMaster, writing, reading
import errno

from pn532pi.interfaces.pn532Interface import Pn532Interface, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, PN532_HOSTTOPN532, \
    PN532_INVALID_FRAME, PN532_POSTAMBLE, PN532_PN532TOHOST, PN532_ACK_WAIT_TIME, PN532_TIMEOUT, \
    PN532_INVALID_ACK

PN532_I2C_ADDRESS =  (0x48 >> 1)

class Pn532I2c(Pn532Interface):
    RPI_BUS0 = 0
    RPI_BUS1 = 1

    def __init__(self, bus: int):
        assert bus in [self.RPI_BUS0, self.RPI_BUS1], "Bus number must be 1 or 0"
        self._wire = None
        self._bus = bus
        self._command = 0

    def begin(self):
        self._wire = I2CMaster(self._bus)
        time.sleep(1)

    def wakeup(self):
        time.sleep(.05) # wait for all ready to manipulate pn532
        return self._wire.transaction(writing(PN532_I2C_ADDRESS, [0]))

    def writeCommand(self, header: bytearray, body: bytearray = bytearray()):
        self._command = header[0]
        data_out = [PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]

        length = len(header) + len(body) + 1 # length of data field: TFI + DATA
        data_out.append(length)
        data_out.append((~length & 0xFF) + 1) # checksum of length

        data_out.append(PN532_HOSTTOPN532)
        dsum = PN532_HOSTTOPN532 + sum(header) + sum(body)  # sum of TFI + DATA

        data_out += list(header)
        data_out += list(body)
        checksum = ((~dsum & 0xFF) + 1) & 0xFF # checksum of TFI + DATA

        data_out += [checksum, PN532_POSTAMBLE]

        DMSG("writeCommand: {}    {}    {}".format(header, body, data_out))

        try:
            # send data
            self._wire.transaction(writing(PN532_I2C_ADDRESS, tuple(data_out)))
        except Exception as e:
            DMSG(e)
            DMSG("\nToo many data to send, I2C doesn't support such a big packet\n")  # I2C max packet: 32 bytes
            return PN532_INVALID_FRAME

        return self._readAckFrame()

    def _getResponseLength(self, timeout: int):
        PN532_NACK = [0, 0, 0xFF, 0xFF, 0, 0]
        timer = 0

        while 1:
            responses = self._wire.transaction(reading(PN532_I2C_ADDRESS, 6))
            data = bytearray(responses[0])
            DMSG('_getResponseLength length frame: {!r}'.format(data))
            if data[0] & 0x1:
              # check first byte --- status
                break # PN532 is ready

            time.sleep(.001)    # sleep 1 ms
            timer+=1
            if ((0 != timeout) and (timer > timeout)):
                return -1


        if (PN532_PREAMBLE != data[1] or # PREAMBLE
            PN532_STARTCODE1 != data[2] or # STARTCODE1
            PN532_STARTCODE2 != data[3]    # STARTCODE2
        ):
            DMSG('Invalid Length frame: {}'.format(data))
            return PN532_INVALID_FRAME

        length = data[4]
        DMSG('_getResponseLength length is {:d}'.format(length))

        # request for last respond msg again
        DMSG('_getResponseLength writing nack: {!r}'.format(PN532_NACK))
        self._wire.transaction(writing(PN532_I2C_ADDRESS, PN532_NACK))

        return length

    def readResponse(self, timeout: int = 1000) -> (int, bytearray):
        t = 0
        length = self._getResponseLength(timeout)
        buf = bytearray()

        if length < 0:
            return length, buf

        # [RDY] 00 00 FF LEN LCS (TFI PD0 ... PDn) DCS 00
        while 1:
            responses = self._wire.transaction(reading(PN532_I2C_ADDRESS, 6 + length + 2))
            data = bytearray(responses[0])
            if (data[0] & 1):
              # check first byte --- status
                break # PN532 is ready

            time.sleep(.001)     # sleep 1 ms
            t+=1
            if ((0 != timeout) and (t> timeout)):
                return -1, buf

        if (PN532_PREAMBLE != data[1] or # PREAMBLE
            PN532_STARTCODE1 != data[2] or # STARTCODE1
            PN532_STARTCODE2 != data[3]    # STARTCODE2
        ):
            DMSG('Invalid Response frame: {}'.format(data))
            return PN532_INVALID_FRAME, buf

        length = data[4]

        if (0 != (length + data[5] & 0xFF)):
         # checksum of length
            DMSG('Invalid Length Checksum: len {:d} checksum {:d}'.format(length, data[5]))
            return PN532_INVALID_FRAME, buf

        cmd = self._command + 1 # response command
        if (PN532_PN532TOHOST != data[6] or (cmd) != data[7]):
            return PN532_INVALID_FRAME, buf

        length -= 2

        DMSG("readResponse read command:  {:x}".format(cmd))

        dsum = PN532_PN532TOHOST + cmd
        buf = data[8:-2]
        DMSG('readResponse response: {!r}\n'.format(buf))
        dsum += sum(buf)

        checksum = data[-2]
        if (0 != (dsum + checksum) & 0xFF):
            DMSG("checksum is not ok: sum {:d} checksum {:d}\n".format(dsum, checksum))
            return PN532_INVALID_FRAME, buf
        # POSTAMBLE data [-1]

        return length, buf

    def _readAckFrame(self) -> int:
        PN532_ACK = [0, 0, 0xFF, 0, 0xFF, 0]

        DMSG("wait for ack at : ")
        DMSG(time.time())
        DMSG('\n')

        t = 0
        while t <= PN532_ACK_WAIT_TIME:
            try:
                responses = self._wire.transaction(reading(PN532_I2C_ADDRESS, len(PN532_ACK) + 1))
                data = bytearray(responses[0])
                if (data[0] & 1):
                    # check first byte --- status
                    break # PN532 is ready
            except IOError as e:
                # As of Python 3.3 IOError is the same as OSError so we should check the error code
                if e.errno != errno.EIO:
                    raise   # Reraise the error   
                # Otherwise do nothing, sleep and try again
            
            time.sleep(.001)    # sleep 1 ms
            t+=1
        else:
            DMSG("Time out when waiting for ACK\n")
            return PN532_TIMEOUT

        DMSG("ready at : ")
        DMSG(time.time())
        DMSG('\n')

        ackBuf = list(data[1:])

        if ackBuf != PN532_ACK:
            DMSG("Invalid ACK {}\n".format(ackBuf))
            return PN532_INVALID_ACK

        return 0
