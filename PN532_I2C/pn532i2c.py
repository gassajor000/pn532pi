import time
from quick2wire.i2c import I2CMaster, writing

from PN532.pn532Interface import pn532Interface, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, PN532_HOSTTOPN532, \
    PN532_INVALID_FRAME, PN532_POSTAMBLE, PN532_PN532TOHOST, PN532_NO_SPACE, PN532_ACK_WAIT_TIME, PN532_TIMEOUT, \
    PN532_INVALID_ACK

PN532_I2C_ADDRESS =  (0x48 >> 1)

class pn532i2c(pn532Interface):
    RPI_BUS0 = 0
    RPI_BUS1 = 1

    def __init__(self, bus: int):
        assert bus in [self.RPI_BUS0, self.RPI_BUS1], "Bus number must be 1 or 0"
        self._wire = None
        self._bus = bus
        self._command = 0

    def begin(self):
        self._wire = I2CMaster()

    def wakeup(self):
        time.sleep(.5) # wait for all ready to manipulate pn532

    def writeCommand(self, header: bytearray, body: bytearray):
        self._command = header[0]
        data_out = [PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]

        length = len(header) + len(body) + 1 # length of data field: TFI + DATA
        data_out.append(length)
        data_out.append(~length + 1) # checksum of length

        data_out.append(PN532_HOSTTOPN532)
        sum = PN532_HOSTTOPN532 # sum of TFI + DATA

        data_out += list(header)
        data_out += list(body)
        checksum = (~sum + 1) & 0xFF # checksum of TFI + DATA

        data_out += [checksum, PN532_POSTAMBLE]

        print("write: ")
        print(header)
        print(body)
        print('\n')


        try:
            # send data
            self._wire.transaction(writing(PN532_I2C_ADDRESS, tuple(data_out)))
        except:
            print("\nToo many data to send, I2C doesn't support such a big packet\n")  # I2C max packet: 32 bytes
            return PN532_INVALID_FRAME

        return self._readAckFrame()

    def _getResponseLength(self, timeout: int):
        PN532_NACK = [0, 0, 0xFF, 0xFF, 0, 0]
        time = 0

        while 1:
            data = self._wire.transaction(self._wire.reading(PN532_I2C_ADDRESS, 6))
            if data[0] & 0x1:
              # check first byte --- status
                break # PN532 is ready

            time.sleep(1)
            time+=1
            if ((0 != timeout) and (time > timeout)):
                return -1


        if (0x00 != data[1] or # PREAMBLE
            0x00 != data[2] or # STARTCODE1
            0xFF != data[3]    # STARTCODE2
        ):

            return PN532_INVALID_FRAME

        length = data[4]

        # request for last respond msg again
        self._wire.transaction(self._wire.writing(PN532_I2C_ADDRESS, PN532_NACK))

        return length

    def readResponse(self, timeout: int = 1000) -> (int, bytearray):
        t = 0
        length = self._getResponseLength(timeout)
        buf = bytearray()

        # [RDY] 00 00 FF LEN LCS (TFI PD0 ... PDn) DCS 00
        while 1:
            data = self._wire.transaction(self._wire.reading(PN532_I2C_ADDRESS, 6 + length + 2))
            if (data[0] & 1):
              # check first byte --- status
                break # PN532 is ready

            time.sleep(1)
            t+=1
            if ((0 != timeout) and (t> timeout)):
                return -1, buf

        if (0x00 != data[1] or # PREAMBLE
            0x00 != data[2] or # STARTCODE1
            0xFF != data[3]    # STARTCODE2
        ):

            return PN532_INVALID_FRAME

        length = data[4]

        if (0 != (length + data[5])):
         # checksum of length
            return PN532_INVALID_FRAME

        cmd = self._command + 1 # response command
        if (PN532_PN532TOHOST != data[6] or (cmd) != data[7]):
            return PN532_INVALID_FRAME, buf

        length -= 2

        print("read:  ")
        print('{:x]'.format(cmd))

        dsum = PN532_PN532TOHOST + cmd
        buf = data[8:-2]
        print(buf)
        print('\n')
        dsum += sum(buf)

        checksum = data[-2]
        if (0 != (dsum + checksum) & 0xFF):
            print("checksum is not ok\n")
            return PN532_INVALID_FRAME, buf
        # POSTAMBLE data [-1]

        return length, buf

    def _readAckFrame(self) -> int:
        PN532_ACK = [0, 0, 0xFF, 0, 0xFF, 0]

        print("wait for ack at : ")
        print(time.time())
        print('\n')

        t = 0
        while 1:
            data = self._wire.transaction(self._wire.reading(PN532_I2C_ADDRESS, len(PN532_ACK) + 1))
            if (data[0] & 1):
              # check first byte --- status
                break # PN532 is ready

            time.sleep(1)
            t+=1
            if (t > PN532_ACK_WAIT_TIME):
                print("Time out when waiting for ACK\n")
                return PN532_TIMEOUT

        print("ready at : ")
        print(time.time())
        print('\n')

        ackBuf = list(data[1:])

        if ackBuf == PN532_ACK:
            print("Invalid ACK\n")
            return PN532_INVALID_ACK

        return 0
