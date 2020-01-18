from serial import Serial
import time

from PN532.pn532Interface import pn532Interface, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, PN532_HOSTTOPN532, \
    PN532_POSTAMBLE, PN532_TIMEOUT, PN532_INVALID_FRAME, PN532_NO_SPACE, PN532_PN532TOHOST, PN532_INVALID_ACK, \
    PN532_ACK_WAIT_TIME
from PN532.pn532_log import DMSG, DMSG_HEX

PN532_WAKEUP = bytearray([0x55, 0x55, 0x00, 0x00, 0x00])

class pn532hsu(pn532Interface):
    RPI_MINI_UART = 0
    RPI_PL011 = 1

    def __init__(self, port: int):
        assert port in [self.RPI_MINI_UART, self.RPI_MINI_UART], 'Invalid RPI UART port %d' % port
        self._serial = Serial('/dev/serial' + str(port), baudrate=115200, timeout=100)
        self._serial.close()
        self.command = 0
    
    def begin(self):
        self._serial.open()
    
    def wakeup(self):
        self._serial.write(PN532_WAKEUP)
    
        #  dump serial buffer 
        if (self._serial.inWaiting()):
            DMSG("Dump serial buffer: ")
        while (self._serial.inWaiting()):
            ret = self._serial.read()
            DMSG_HEX(ret)

    def writeCommand(self, header: bytearray, body: bytearray = bytearray()) -> int:

        # dump serial buffer 
        if (self._serial.inWaiting()):
            DMSG("Dump serial buffer: ")
        while (self._serial.inWaiting()):
            ret = self._serial.read()
            DMSG_HEX(ret)

        self.command = header[0]

        self._serial.write(PN532_WAKEUP)    # Extra long Preamble in case PN532 is in low VBat mode
        self._serial.write(bytearray([PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]))
    
        length = len(header) + len(body) + 1 # length of data field: TFI + DATA
        self._serial.write(bytearray([length, (~length + 1) & 0xff, PN532_HOSTTOPN532]))  # checksum of length
    
        dsum = PN532_HOSTTOPN532 + sum(header) + sum(body)
    
        DMSG("\nWrite: ")
    
        self._serial.write(header)
    
        checksum = (~dsum + 1) & 0xff  # checksum of TFI + DATA
        self._serial.write(bytearray([checksum, PN532_POSTAMBLE]))
    
        return self.readAckFrame()

    def readResponse(self, timeout: int = 1000) -> (int, bytearray):
    
        DMSG("\nRead:  ")
    
        # Frame Preamble and Start Code 
        num, tmp = self.receive(3, timeout)
        if (num <= 0):
            return PN532_TIMEOUT, tmp
        if (0 != tmp[0] or 0 != tmp[1] or 0xFF != tmp[2]):
            DMSG("Preamble error")
            return PN532_INVALID_FRAME, bytearray()
    
        # receive length and check 
        num, length = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT, length
        if (0 != (length[0] + length[1]) & 0xff):
            DMSG("Length error")
            return PN532_INVALID_FRAME, bytearray()
        length[0] -= 2
        if (length[0] > len):
            return PN532_NO_SPACE, bytearray()

        # receive self.command byte 
        cmd = self.command + 1 # response self.command
        num, tmp = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT, tmp
        if (PN532_PN532TOHOST != tmp[0] or cmd != tmp[1]):
            DMSG("Command error")
            return PN532_INVALID_FRAME, bytearray()

        num, buf = self.receive(length[0], timeout)
        if (num != length[0]):
            return PN532_TIMEOUT, buf
        dsum = PN532_PN532TOHOST + cmd + sum(buf)

        # checksum and postamble 
        num, tmp = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT, tmp
        if (0 != (dsum + tmp[0]) & 0xff or 0 != tmp[1]):
            DMSG("Checksum error")
            return PN532_INVALID_FRAME, bytearray()

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
        self._serial.timeout = timeout / 1000.0

        while (read_bytes < length):
            data = self._serial.read()
            if (data):
                rx_data += data
                read_bytes += len(data)
                break

            else:  # Timed out
                if (read_bytes):
                    return read_bytes, rx_data
                else:
                    return PN532_TIMEOUT, bytearray()

        return read_bytes, rx_data
