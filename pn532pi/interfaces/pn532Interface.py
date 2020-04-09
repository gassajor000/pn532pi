
PN532_PREAMBLE                = (0x00)
PN532_STARTCODE1              = (0x00)
PN532_STARTCODE2              = (0xFF)
PN532_POSTAMBLE               = (0x00)
PN532_HOSTTOPN532             = (0xD4)
PN532_PN532TOHOST             = (0xD5)
PN532_ACK_WAIT_TIME           = (10)  # ms, timeout of waiting for ACK
PN532_INVALID_ACK             = (-1)
PN532_TIMEOUT                 = (-2)
PN532_INVALID_FRAME           = (-3)
PN532_NO_SPACE                = (-4)


def REVERSE_BITS_ORDER(b):
    b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
    b = (b & 0xCC) >> 2 | (b & 0x33) << 2
    b = (b & 0xAA) >> 1 | (b & 0x55) << 1
    return b

class Pn532Interface:
    def begin(self):
        raise NotImplementedError('This function is virtual')

    def wakeup(self):
        raise NotImplementedError('This function is virtual')

    def writeCommand(self, header: bytearray, body: bytearray = bytearray()) -> int:
        """
        Write a command and check ack
        :param header:  packet header
        :param body:    packet body
        :return:   0 success, not 0 failed
        """
        raise NotImplementedError('This function is virtual')

    def readResponse(self, timeout: int = 1000) -> (int, bytearray):
        """
        Read the response of a command, strip prefix and suffix
        :param timeout: max time to wait, 0 means no timeout
        :return: (>=0     length of response without prefix an
                    <0      failed to read response, response)
        """
        raise NotImplementedError('This function is virtual')
