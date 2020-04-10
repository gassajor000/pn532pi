from serial import Serial

from pn532pi.interfaces.pn532Interface import Pn532Interface, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, PN532_HOSTTOPN532, \
    PN532_POSTAMBLE, PN532_TIMEOUT, PN532_INVALID_FRAME, PN532_PN532TOHOST, PN532_INVALID_ACK, \
    PN532_ACK_WAIT_TIME
from pn532pi.nfc.pn532_log import DMSG, DMSG_HEX

PN532_WAKEUP = bytearray([0x55, 0x00, 0x00, 0x55])

class Pn532Hsu(Pn532Interface):
    RPI_MINI_UART = 0
    RPI_PL011 = 1

    def __init__(self, port: int):
        assert port in [self.RPI_MINI_UART, self.RPI_PL011], 'Invalid RPI UART port %d' % port
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
            ret = self._serial.read()
            DMSG_HEX(ret)

    def writeCommand(self, header: bytearray, body: bytearray = bytearray()) -> int:

        # dump serial buffer 
        if (self._serial.inWaiting()):
            DMSG("Dump serial buffer: ")
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
        self._serial.write(body)

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
        num, tmp = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT, tmp

        length, lchksm = tmp[0], tmp[1]        
        if (0 != (length + lchksm) & 0xff):
            DMSG("Length error")
            return PN532_INVALID_FRAME, bytearray()
        length -= 2

        # receive self.command byte 
        cmd = self.command + 1 # response self.command
        num, tmp = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT, tmp
        if (PN532_PN532TOHOST != tmp[0] or cmd != tmp[1]):
            DMSG("Command error")
            return PN532_INVALID_FRAME, bytearray()

        num, buf = self.receive(length, timeout)
        if (num != length):
            return PN532_TIMEOUT, buf
        dsum = PN532_PN532TOHOST + cmd + sum(buf)

        # checksum and postamble 
        num, tmp = self.receive(2, timeout)
        if (num <= 0):
            return PN532_TIMEOUT, tmp
        if (0 != (dsum + tmp[0]) & 0xff or 0 != tmp[1]):
            DMSG("Checksum error")
            return PN532_INVALID_FRAME, bytearray()

        return length, buf

    def readAckFrame(self):
        PN532_ACK = bytearray([0, 0, 0xFF, 0, 0xFF, 0])
    
        DMSG("\nAck: ")
    
        num, ackBuf = self.receive(len(PN532_ACK), PN532_ACK_WAIT_TIME)
        if (num<= 0):
            DMSG("Timeout\n")
            return PN532_TIMEOUT

        if (ackBuf != PN532_ACK):
            DMSG("Invalid\n")
            return PN532_INVALID_ACK
        return 0


    def receive(self, num: int, timeout: int) -> (int, bytearray):
        """
        Receive data
        :param num: number expecting to receive.
        :para timeout: time to receive data (milliseconds)
        :returns: (num_read, data)
                    num: int, >= 0 number of bytes received, < 0 Error
                    data: bytearray, data received
        """
        
        self._serial.timeout = timeout / 1000.0
        rx_data = self._serial.read(num)  
        read_bytes = len(rx_data)

        if read_bytes < num:
            return PN532_TIMEOUT, rx_data


        return read_bytes, rx_data
