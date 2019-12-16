from PN532.macLink import macLink
from PN532.pn532 import pn532

# LLCP PDU Type Values

PDU_SYMM = 0x00
PDU_PAX = 0x01
PDU_CONNECT = 0x04
PDU_DISC = 0x05
PDU_CC = 0x06
PDU_DM = 0x07
PDU_I = 0x0c
PDU_RR = 0x0d

LLCP_DEFAULT_DSAP     = 0x04
LLCP_DEFAULT_TIMEOUT  = 20000
LLCP_DEFAULT_SSAP     = 0x20


def getPType(buf) -> int:
    return ((buf[0] & 0x3) << 2) + (buf[1] >> 6)


def getSSAP(buf):
    return buf[1] & 0x3f


def getDSAP(buf):
    return buf[0] >> 2

class llcp:
    SYMM_PDU = [0, 0]

    def __init__(self, interface: pn532):
        self.link = macLink(interface)
        self.ns = 0
        self.nr = 0

    def activate(self, timeout: int):
        return self.link.activateAsTarget(timeout)
    
    def waitForConnection(self, timeout: int) -> int:
        type = 0
    
        self.mode = 1
        self.ns = 0
        self.nr = 0
    
        # Get CONNECT PDU
        print("wait for a CONNECT PDU\n")
        while 1:
            status, data = self.link.read()
            if (2 > status):
                return -1

            type = getPType(data)
            if (PDU_CONNECT == type):
                break
            elif (PDU_SYMM == type):
                if (not self.link.write(bytearray(self.SYMM_PDU))):
                    return -2
            else:
                return -3


        # Put CC PDU
        print("put a CC(Connection Complete) PDU to response the CONNECT PDU\n")
        ssap = getDSAP(data)
        dsap = getSSAP(data)
        header = bytearray([
        (dsap << 2) + ((PDU_CC >> 2) & 0x3),
        ((PDU_CC & 0x3) << 6) + ssap,
        ])
        if (not self.link.write(header)):
            return -2

        return 1

    def waitForDisconnection(self, timeout: int) -> int:
        type = 0
    
        # Get DISC PDU
        print("wait for a DISC PDU\n")
        while 1:
            status, data = self.link.read()
            if (2 > status):
                return -1

            type = getPType(data)
            if (PDU_DISC == type):
                break
            elif (PDU_SYMM == type):
                if (not self.link.write(bytearray(self.SYMM_PDU))):
                    return -2
            else:
                return -3


        # Put DM PDU
        print("put a DM(Disconnect Mode) PDU to response the DISC PDU\n")
        # ssap = getDSAP(headerBuf)
        # dsap = getSSAP(headerBuf)
        header = bytearray([
            (self.dsap << 2) + (PDU_DM >> 2),
            ((PDU_DM & 0x3) << 6) + self.ssap,
        ])
        if (not self.link.write(header)):
            return -2

        return 1

    def connect(self, timeout: int) -> int:
        type = 0
    
        self.mode = 0
        self.dsap = LLCP_DEFAULT_DSAP
        self.ssap = LLCP_DEFAULT_SSAP
        self.ns = 0
        self.nr = 0
    
        # try to get a SYMM PDU
        status, data = self.link.read()
        if (2 > status):
            return -1
        type = getPType(data)
        if (PDU_SYMM != type):
            return -1

        # put a CONNECT PDU
        header = bytearray([
            (LLCP_DEFAULT_DSAP << 2) + (PDU_CONNECT >> 2),
            ((PDU_CONNECT & 0x03) << 6) + LLCP_DEFAULT_SSAP,
        ])
        body = bytearray("  urn:nfc:sn:snep")
        body[0] = 0x06
        body[1] = len(body) - 2 - 1
        if (self.link.write(header, body)):
            return -2

        # wait for a CC PDU
        print("wait for a CC PDU\n")
        while 1:
            status, data = self.link.read()
            if (2 > status):
                return -1

            type = getPType(data)
            if (PDU_CC == type):
                break
            elif (PDU_SYMM == type):
                if (not self.link.write(bytearray(self.SYMM_PDU))):
                    return -2
            else:
                return -3

        return 1

    def disconnect(self, timeout: int) -> int:
        type = 0
    
        # try to get a SYMM PDU
        status, data = self.link.read()
        if (2 > status):
            return -1
        type = getPType(data)
        if (PDU_SYMM != type):
            return -1

        # put a DISC PDU
        header = bytearray([
            (LLCP_DEFAULT_DSAP << 2) + (PDU_DISC >> 2),
            ((PDU_DISC & 0x03) << 6) + LLCP_DEFAULT_SSAP,
        ])
        if (self.link.write(header)):
            return -2

        # wait for a DM PDU
        print("wait for a DM PDU\n")
        while 1:
            status, data = self.link.read()
            if (2 > status):
                return -1

            type = getPType(data)
            if (PDU_CC == type):
                break
            elif (PDU_DM == type):
                if (not self.link.write(bytearray(self.SYMM_PDU))):
                    return -2
            else:
                return -3

        return 1

    def write(self, header: bytearray, body: bytearray = bytearray()) -> bool:

        if (self.mode):
            # Get a SYMM PDU
            status, data = self.link.read()
            if (2 != status):
                return False

        header.reverse()

        full_header = bytearray([
            (self.dsap << 2) + (PDU_I >> 2),
            ((PDU_I & 0x3) << 6) + self.ssap,
            (self.ns << 4) + self.nr,
        ]) + header

        if (not self.link.write(full_header, body)):
            return False

        self.ns += 1
    
        # Get a RR PDU
        status = 0
        while 1:
            status, data = self.link.read()
            if (2 > status):
                return False

            type = getPType(data)
            if (PDU_RR == type):
                break
            elif (PDU_SYMM == type):
                if (not self.link.write(bytearray(self.SYMM_PDU))):
                    return False
            else:
                return False

        if (not self.link.write(bytearray(self.SYMM_PDU))):
            return False

        return True

    def read(self) -> (int, bytearray):
        # Get INFO PDU
        while 1:
            status, data = self.link.read()
            if (2 > status):
                return (-1, bytearray())

            type = getPType(data)
            if (PDU_I == type):
                break
            elif (PDU_SYMM == type):
                if (not self.link.write(bytearray(self.SYMM_PDU))):
                    return -2, bytearray()
            else:
                return -3, bytearray()

        blen = status - 3
        self.ssap = getDSAP(data)
        self.dsap = getSSAP(data)

        header = bytearray([
        (self.dsap << 2) + (PDU_RR >> 2),
        ((PDU_RR & 0x3) << 6) + self.ssap,
        (data[2] >> 4) + 1,
        ])

        if (not self.link.write(header)):
            return -2, bytearray()

        self.nr += 1
    
        return (blen, data[3:])