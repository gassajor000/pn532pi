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

    def write(self, data):
        self._spi.transfer(data)

    def read(self):
        return self._spi.transfer(0)


    def __init__(self, ss: int):
        self._command = 0
        self._ss = ss
        self._spi = SpiDev()
        assert ss < 2, 'Chip select must be 1 or 0'

    def begin(self):
        self._spi.open(RPI_BUS0, self._ss)
        self._spi.mode = SPI_MODE0  # PN532 only supports mode0
        self._spi.lsbfirst = True
        self._spi.max_speed_hz = 5000000 # 5 MHz

    def wakeup(self) -> None:
        self._spi.cshigh = False
        time.sleep(2)
        self._spi.cshigh = True

    def writeCommand(self, header: str, hlen: int, body: str, blen: int) -> int:
        self._command = header[0]
        self.writeFrame(header, hlen, body, blen)

        timeout = PN532_ACK_WAIT_TIME
        while (not self.isReady()):
            time.sleep(1)
            timeout -= 1
            if (0 == timeout):
                print("Time out when waiting for ACK\n")
                return -2
        if (self.readAckFrame()):
            print("Invalid ACK\n")
            return PN532_INVALID_ACK

        return 0

    def readResponse(self, buf: bytearray, blen: int, timeout: int):
        time = 0
        while (not self.isReady()):
            time.sleep(1)
            time += 1
            if (time > timeout):
                return PN532_TIMEOUT

        digitalWrite(self._ss, LOW)
        time.sleep(1)

        result = 0
        while (1):
            write(DATA_READ)

            if (0x00 != read() or # PREAMBLE
                0x00 != read()  or # STARTCODE1
                0xFF != read() # STARTCODE2
                ):
    
                result = PN532_INVALID_FRAME
                break
    
            length = read()
            if (0 != (uint8_t)(length + read())): # checksum of length
                result = PN532_INVALID_FRAME
                break
    
            cmd = self._command + 1 # response command
            if (PN532_PN532TOHOST != read() or (cmd) != read()):
                result = PN532_INVALID_FRAME
                break
    
            print("read:  {:x}".format(cmd))

            length -= 2
            if (length > len):
                for i in range(length):
                        print_HEX(read()) # dump message
                print("\nNot enough space\n")
                read()
                read()
                result = PN532_NO_SPACE # not enough space
                break
    
            sum = PN532_PN532TOHOST + cmd
            for  i in range(length):
                buf[i] = read()
                sum += buf[i]
    
                print_HEX(buf[i])
            print('\n')
    
            checksum = read()
            if (0 != (uint8_t)(sum + checksum)):
                print("checksum is not ok\n")
                result = PN532_INVALID_FRAME
                break
            read() # POSTAMBLE
    
            result = length

        digitalWrite(self._ss, HIGH)

        return result

    def isReady(self) -> int:
        digitalWrite(self._ss, LOW)

        write(STATUS_READ)
        status = read() & 1
        digitalWrite(self._ss, HIGH)
        return status

    def writeFrame(self, header: str, hlen: int, body: str, blen: int):
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

    def readAckFrame(self):
        PN532_ACK = [0, 0, 0xFF, 0, 0xFF, 0]

        ackBuf = []

        digitalWrite(_ss, LOW)
        time.sleep(1)
        write(DATA_READ)

        for i in range(PN532_ACK):
            ackBuf[i] = read()

        digitalWrite(self._ss, HIGH)

        return ackBuf == PN532_ACK