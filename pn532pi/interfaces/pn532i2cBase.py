import time
import errno
from pn532pi.nfc.pn532_log import DMSG
from pn532pi.interfaces.pn532Interface import Pn532Interface, PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2, PN532_HOSTTOPN532, \
    PN532_INVALID_FRAME, PN532_POSTAMBLE, PN532_PN532TOHOST, PN532_ACK_WAIT_TIME, PN532_TIMEOUT, \
    PN532_INVALID_ACK

PN532_I2C_ADDRESS =  (0x48 >> 1)

class Pn532I2cBase(Pn532Interface):
    def __init__(self):
        self._command = 0
    
    def begin(self):
        time.sleep(1)  # Allow time for the PN532 to initialize.

    def wakeup(self):
        time.sleep(0.05)
        self._write(b'\x00')

    def writeCommand(self, header: bytearray, body: bytearray = bytearray()):
        self._command = header[0]
        data_out = [PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]

        length = len(header) + len(body) + 1
        data_out.append(length)
        data_out.append((~length & 0xFF) + 1)

        data_out.append(PN532_HOSTTOPN532)
        dsum = PN532_HOSTTOPN532 + sum(header) + sum(body)

        data_out += list(header)
        data_out += list(body)
        checksum = ((~dsum & 0xFF) + 1) & 0xFF
        data_out += [checksum, PN532_POSTAMBLE]

        DMSG(f"writeCommand: {header} {body} {data_out}")
        
        try:
            self._write(bytes(data_out))
        except Exception as e:
            DMSG(e)
            return PN532_INVALID_FRAME

        return self._readAckFrame()
    
    def _getResponseLength(self, timeout: int):
        PN532_NACK = [0, 0, 0xFF, 0xFF, 0, 0]
        t = 0

        while True:
            data = self._read(6)
            DMSG(f'_getResponseLength length frame: {data}')
            if data and data[0] & 0x1:
                break
            time.sleep(0.001)
            t += 1
            if timeout and t > timeout:
                return -1

        if data[1:4] != bytes([PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]):
            return PN532_INVALID_FRAME

        length = data[4]
        self._write(bytes(PN532_NACK))
        return length

    def readResponse(self, timeout: int = 1000):
        t = 0
        length = self._getResponseLength(timeout)
        buf = bytearray()
        if length < 0:
            return length, buf

        while True:
            data = self._read(6 + length + 2)
            if data and data[0] & 0x1:
                break
            time.sleep(0.001)
            t += 1
            if timeout and t > timeout:
                return -1, buf

        if data[1:4] != bytes([PN532_PREAMBLE, PN532_STARTCODE1, PN532_STARTCODE2]):
            return PN532_INVALID_FRAME, buf

        length = data[4]
        if (length + data[5]) & 0xFF != 0:
            return PN532_INVALID_FRAME, buf

        cmd = self._command + 1
        if data[6] != PN532_PN532TOHOST or data[7] != cmd:
            return PN532_INVALID_FRAME, buf

        buf = data[8:-2]
        checksum = data[-2]
        if (sum(buf) + PN532_PN532TOHOST + cmd + checksum) & 0xFF != 0:
            return PN532_INVALID_FRAME, buf

        return length, buf
    
    def _readAckFrame(self):
        PN532_ACK = [0, 0, 0xFF, 0, 0xFF, 0]
        t = 0
        while t <= PN532_ACK_WAIT_TIME:
            data = self._read(len(PN532_ACK) + 1)
            if data and data[0] & 1:
                break
            time.sleep(0.001)
            t += 1
        else:
            return PN532_TIMEOUT

        ackBuf = list(data[1:])
        if ackBuf != PN532_ACK:
            return PN532_INVALID_ACK
        return 0

    def _write(self, data: bytes):
        raise NotImplementedError("_write must be implemented in subclass")
    
    def _read(self, num_bytes: int):
        raise NotImplementedError("_read must be implemented in subclass")