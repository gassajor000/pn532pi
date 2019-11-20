import time

from PN532.pn532Interface import pn532Interface, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, PN532_HOSTTOPN532, \
    PN532_INVALID_FRAME, PN532_POSTAMBLE, PN532_PN532TOHOST, PN532_NO_SPACE, PN532_ACK_WAIT_TIME, PN532_TIMEOUT, \
    PN532_INVALID_ACK

PN532_I2C_ADDRESS =  (0x48 >> 1)

class pn532i2c(pn532Interface):
    def __init__(self, wire: I2C_CLASS):
        self._wire = wire
        self._command = 0

    def begin(self):
        self._wire.begin()

    def wakeup(self):
        time.sleep(.5) # wait for all ready to manipulate pn532

    def writeCommand(self, header: str, hlen: int, body: str, blen: int = 0):
        self._command = header[0]
        self._wire.beginTransmission(PN532_I2C_ADDRESS)

        write(PN532_PREAMBLE)
        write(PN532_STARTCODE1)
        write(PN532_STARTCODE2)

        length = hlen + blen + 1 # length of data field: TFI + DATA
        write(length)
        write(~length + 1) # checksum of length

        write(PN532_HOSTTOPN532)
        sum = PN532_HOSTTOPN532 # sum of TFI + DATA

        print("write: ")

        for i in range(hlen):
            if (write(header[i])):
                sum += header[i]

                print(header[i])
            else:
                print("\nToo many data to send, I2C doesn't support such a big packet\n") # I2C max packet: 32 bytes
                return PN532_INVALID_FRAME

        for i in range(blen):
            if (write(body[i])):
                sum += body[i]

                print(body[i])
            else:
                print("\nToo many data to send, I2C doesn't support such a big packet\n") # I2C max packet: 32 bytes
                return PN532_INVALID_FRAME

        checksum = (~sum + 1) & 0xFF # checksum of TFI + DATA
        write(checksum)
        write(PN532_POSTAMBLE)

        self._wire.endTransmission()

        print('\n')

        return self.readAckFrame()

    def getResponseLength(self, buf: bytearray, length: int, timeout: int):
        PN532_NACK = [0, 0, 0xFF, 0xFF, 0, 0]
        time = 0

        while 1:
            if self._wire.requestFrom(PN532_I2C_ADDRESS, 6):
                if (read() & 1):
                          # check first byte --- status
                    break # PN532 is ready


            time.sleep(1)
            time+=1
            if ((0 != timeout) && (time > timeout)):
                return -1


        if (0x00 != read() || # PREAMBLE
            0x00 != read() || # STARTCODE1
            0xFF != read()    # STARTCODE2
        ):

            return PN532_INVALID_FRAME

        length = read()

        # request for last respond msg again
        self._wire.beginTransmission(PN532_I2C_ADDRESS)
        for i in PN532_NACK:
            write(i)
        self._wire.endTransmission()

        return length

    def readResponse(self, buf: bytearray, blen: int, timeout: int = 1000) -> int:
        t = 0
        length = self.getResponseLength(buf, blen, timeout)

        # [RDY] 00 00 FF LEN LCS (TFI PD0 ... PDn) DCS 00
        while 1:
            if (self._wire.requestFrom(PN532_I2C_ADDRESS, 6 + length + 2)):
                if (read() & 1):
                          # check first byte --- status
                    break # PN532 is ready

            time.sleep(1)
            t+=1
            if ((0 != timeout) && (t> timeout)):
                return -1

        if (0x00 != read() or # PREAMBLE
            0x00 != read() or # STARTCODE1
            0xFF != read()    # STARTCODE2
        ):

            return PN532_INVALID_FRAME

        length = read()

        if (0 != (uint8_t)(length + read())):
         # checksum of length
            return PN532_INVALID_FRAME

        cmd = self._command + 1 # response command
        if (PN532_PN532TOHOST != read() or (cmd) != read()):
            return PN532_INVALID_FRAME

        length -= 2
        if (length > blen):
            return PN532_NO_SPACE # not enough space

        print("read:  ")
        print('{:x]'.format(cmd))

        sum = PN532_PN532TOHOST + cmd
        for i in range(length):
            buf[i] = read()
            sum += buf[i]

            print(hex(buf[i]))
        print('\n')

        checksum = read()
        if (0 != (uint8_t)(sum + checksum)):
            print("checksum is not ok\n")
            return PN532_INVALID_FRAME
        read() # POSTAMBLE

        return length

    def readAckFrame(self) -> int:
        PN532_ACK = [0, 0, 0xFF, 0, 0xFF, 0]
        ackBuf = []

        print("wait for ack at : ")
        print(millis())
        print('\n')

        t = 0
        while 1:
            if (self._wire.requestFrom(PN532_I2C_ADDRESS, sizeof(PN532_ACK) + 1)):
                if (read() & 1):
                          # check first byte --- status
                    break # PN532 is ready

            time.sleep(1)
            t+=1
            if (t > PN532_ACK_WAIT_TIME):
                print("Time out when waiting for ACK\n")
                return PN532_TIMEOUT

        print("ready at : ")
        print(millis())
        print('\n')

        for i in range(len(PN532_ACK)):
            ackBuf[i] = read()

        if ackBuf == PN532_ACK:
            print("Invalid ACK\n")
            return PN532_INVALID_ACK

        return 0
