
import time

from PN532.pn532Interface import pn532Interface, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, PN532_HOSTTOPN532, \
    PN532_POSTAMBLE, PN532_TIMEOUT, PN532_INVALID_FRAME, PN532_NO_SPACE, PN532_PN532TOHOST, PN532_INVALID_ACK, \
    PN532_ACK_WAIT_TIME
from PN532.pn532_log import DMSG, DMSG_HEX


class pn532hsu(pn532Interface):
    def __init__(self, serial: HardwareSerial):
        self._serial = serial
        self.command = 0
    
    def begin(self):
        self._serial.begin(115200)
    
    def wakeup(self):
        self._serial.write(0x55)
        self._serial.write(0x55)
        self._serial.write(0x00)
        self._serial.write(0x00)
        self._serial.write(0x00)
    
        #  dump serial buffer 
        if (self._serial.available()):
            DMSG("Dump serial buffer: ")
        while (self._serial.available()):
            ret = self._serial.read()
            DMSG_HEX(ret)

    def writeCommand(self, header: bytearray, body: bytearray = bytearray()) -> int:

        # dump serial buffer 
        if (self._serial.available()):
            DMSG("Dump serial buffer: ")
        while (self._serial.available()):
            ret = self._serial.read()
            DMSG_HEX(ret)

        self.command = header[0]
    
        self._serial.write(PN532_PREAMBLE)
        self._serial.write(PN532_STARTCODE1)
        self._serial.write(PN532_STARTCODE2)
    
        length = len(header) + len(body) + 1 # length of data field: TFI + DATA
        self._serial.write(length)
        self._serial.write(~length + 1)  # checksum of length
    
        self._serial.write(PN532_HOSTTOPN532)
        dsum = PN532_HOSTTOPN532 + sum(header) + sum(body)
    
        DMSG("\nWrite: ")
    
        self._serial.write(header, len(header))
    
        checksum = ~dsum + 1  # checksum of TFI + DATA
        self._serial.write(checksum)
        self._serial.write(PN532_POSTAMBLE)
    
        return self.readAckFrame()

    def readResponse(self, timeout: int = 1000) -> (int, bytearray):
    
        DMSG("\nRead:  ")
    
        # Frame Preamble and Start Code 
        num, tmp = self.receive(3, timeout)
        if (num <= 0):
            return PN532_TIMEOUT
        if (0 != tmp[0] or 0 != tmp[1] or 0xFF != tmp[2]):
            DMSG("Preamble error")
            return PN532_INVALID_FRAME
    
        # receive length and check 
        num, length = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT
        if (0 != (length[0] + length[1]) & 0xff):
            DMSG("Length error")
            return PN532_INVALID_FRAME
        length[0] -= 2
        if (length[0] > len):
            return PN532_NO_SPACE

        # receive self.command byte 
        cmd = self.command + 1 # response self.command
        num, tmp = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT
        if (PN532_PN532TOHOST != tmp[0] or cmd != tmp[1]):
            DMSG("Command error")
            return PN532_INVALID_FRAME

        num, buf = self.receive(length[0], timeout)
        if (num != length[0]):
            return PN532_TIMEOUT
        dsum = PN532_PN532TOHOST + cmd + sum(buf)

        # checksum and postamble 
        num, tmp = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT
        if (0 != (dsum + tmp[0]) & 0xff or 0 != tmp[1]):
            DMSG("Checksum error")
            return PN532_INVALID_FRAME

        return length[0]

    def readAckFrame(self):
        PN532_ACK = bytearray([0, 0, 0xFF, 0, 0xFF, 0])
    
        DMSG("\nAck: ")
    
        num, ackBuf = self.receive(len(PN532_ACK), PN532_ACK_WAIT_TIME)
        if (num<= 0):
            DMSG("Timeout\n")
            return PN532_TIMEOUT

        if (ackBuf == PN532_ACK):
            DMSG("Invalid\n")
            return PN532_INVALID_ACK
        return 0


    def receive(self, length: int, timeout: int) -> (int, bytearray):
        """
        Receive data
        :param len: length expect to receive.
        :para timeout: time to receive data (milliseconds)
        :returns: (num, data)
                    num: int, >= 0 number of bytes received, < 0 Error
                    data: bytearray, data received
        """
        read_bytes = 0
        rx_data = bytearray()

        while (read_bytes < length):
            start_time = time.time()
            end_time = start_time + timeout/1000.0
            data = bytearray()
            while ((timeout == 0) or time.time() < end_time):
                data = self._serial.read()
                if (data):
                    rx_data += data
                    read_bytes += len(data)
                    break

            if (not data):  # Timed out
                if (read_bytes):
                    return read_bytes, rx_data
                else:
                    return PN532_TIMEOUT, bytearray()

        return read_bytes, rx_data
