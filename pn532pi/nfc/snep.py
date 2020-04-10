from pn532pi.nfc.llcp import Llcp
from pn532pi.nfc.pn532 import Pn532
from pn532pi.nfc.pn532_log import DMSG

SNEP_DEFAULT_VERSION	= 0x10	# Major: 1, Minor: 0

SNEP_REQUEST_PUT		= 0x02
SNEP_REQUEST_GET		= 0x01

SNEP_RESPONSE_SUCCESS	= 0x81
SNEP_RESPONSE_REJECT	= 0xFF


class Snep:
    def __init__(self, interface: Pn532):
        self.llcp = Llcp(interface)

    def write(self, buf: bytearray, timeout: int = 0) -> int:
        """
        Write a SNEP packet, the packet should be less than (255 - 2 - 3) bytes
        :param:    buf     the buffer to contain the packet
        :param:    len     length of the buffer
        :param:    timeout max time to wait, 0 means no timeout
        :returns:   >0      success
                    =0      timeout
                    <0      failed
        """
        if (0 >= self.llcp.activate(timeout)):
            DMSG("failed to activate PN532 as a target\n")
            return -1
    
        if (0 >= self.llcp.connect(timeout)):
            DMSG("failed to set up a connection\n")
            return -2
    
        # response a success SNEP message
        header = bytearray([
        SNEP_DEFAULT_VERSION,
        SNEP_REQUEST_PUT,
        0,
        0,
        0,
        len(buf),
        ])

        if (0 >= self.llcp.write(header, buf)):
            return -3
    
        status, rbuf = self.llcp.read() 
        if (6 > status):
            return -4
    
        # check SNEP version
        if (SNEP_DEFAULT_VERSION != rbuf[0]):
            DMSG("The received SNEP message's major version is different\n")
            # Todo: send Unsupported Version response
            return -4
    
        # expect a put request
        if (SNEP_RESPONSE_SUCCESS != rbuf[1]):
            DMSG("Expect a success response\n")
            return -4
    
        self.llcp.disconnect(timeout)
    
        return 1

    def read(self, timeout: int = 0) -> (int, bytearray):
        """
        read a SNEP packet, the packet will be less than (255 - 2 - 3) bytes
        :param:    buf     the buffer to contain the packet
        :param:    len     length of the buffer
        :param:    timeout max time to wait, 0 means no timeout
        :returns: (status, data)
                    status: int, >=0 length of the packet, <0 failed
                    data: : bytearray, data read
        """
        if (0 >= self.llcp.activate(timeout)) :
            DMSG("failed to activate PN532 as a target\n")
            return -1, bytearray()

        if (0 >= self.llcp.waitForConnection(timeout)):
            DMSG("failed to set up a connection\n")
            return -2, bytearray()

        status, buf = self.llcp.read()
        if (6 > status):
            return -3, bytearray()

        # check SNEP version

        # in case of platform specific bug, shift SNEP message for 4 bytes.
        # tested on Nexus 5, Android 5.1
        if (SNEP_DEFAULT_VERSION != buf[0] and SNEP_DEFAULT_VERSION == buf[4]):
            buf = buf[4:]

        if (SNEP_DEFAULT_VERSION != buf[0]):
                DMSG("SNEP->read: The received SNEP message's major version is different, me: ")
                DMSG(SNEP_DEFAULT_VERSION)
                DMSG(", their: ")
                DMSG(buf[0])
                DMSG("\n")
                # To-do: send Unsupported Version response
                return -4, bytearray()

        # expect a put request
        if (SNEP_REQUEST_PUT != buf[1]):
            DMSG("Expect a put request\n")
            return -4, bytearray()

        # check message's length
        length = (buf[2] << 24) + (buf[3] << 16) + (buf[4] << 8) + buf[5]
        # length should not be more than 244 (header + body < 255, header = 6 + 3 + 2)
        if (length > (status - 6)):
            DMSG("The SNEP message is too large: {} {}".format(length, length -6))
            return -4

        buf = buf[6:]

        # response a success SNEP message
        header = bytearray([
            SNEP_DEFAULT_VERSION,
            SNEP_RESPONSE_SUCCESS,
            0,
            0,
            0,
            0,
        ])

        self.llcp.write(header)

        return length, buf
