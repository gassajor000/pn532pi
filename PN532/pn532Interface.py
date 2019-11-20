
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

class pn532Interface:
    def begin(self):
        raise NotImplementedError('This function is virtual')
    def wakeup(self):
        raise NotImplementedError('This function is virtual')

    """
    * @brief    write a command and check ack
    * @param    header  packet header
    * @param    hlen    length of header
    * @param    body    packet body
    * @param    blen    length of body
    * @return   0       success
    *           not 0   failed
    """
    def writeCommand(self, header: str, hlen: int, body: str, blen: int = 0) -> int:
        raise NotImplementedError('This function is virtual')

    """
    * @brief    read the response of a command, strip prefix and suffix
    * @param    buf     to contain the response data
    * @param    len     length to read
    * @param    timeout max time to wait, 0 means no timeout
    * @return   >=0     length of response without prefix and suffix
    *           <0      failed to read response
    """
    def readResponse(self, buf: bytearray, blen: int, timeout: int = 1000) -> int:
        raise NotImplementedError('This function is virtual')
