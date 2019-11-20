from PN532.pn532Interface import pn532Interface

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

    def __init__(self, interface: pn532Interface):
        self.link = MACLink(interface)
        self.headerBuf, self.headerBufLen = interface.getHeaderBuffer()
        self.ns = 0
        self.nr = 0


    def getHeaderBuffer(self) -> (int, str):
        buf, blen = self.link.getHeaderBuffer()
        blen -= 3       # I PDU header has 3 bytes
        return buf, blen

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
            if (2 > self.link.read(self.headerBuf, self.headerBufLen)):
                return -1

            type = getPType(self.headerBuf)
            if (PDU_CONNECT == type):
                break
            elif (PDU_SYMM == type):
                if ( not self.link.write(self.SYMM_PDU, sizeof(self.SYMM_PDU))):
                    return -2
            else:
                return -3


        # Put CC PDU
        print("put a CC(Connection Complete) PDU to response the CONNECT PDU\n")
        ssap = getDSAP(self.headerBuf)
        dsap = getSSAP(self.headerBuf)
        self.headerBuf[0] = (dsap << 2) + ((PDU_CC >> 2) & 0x3)
        self.headerBuf[1] = ((PDU_CC & 0x3) << 6) + ssap
        if (not self.link.write(self.headerBuf, 2)):
            return -2

        return 1

    def waitForDisconnection(self, timeout: int) -> int:
        type = 0
    
        # Get DISC PDU
        print("wait for a DISC PDU\n")
        while 1:
            if (2 > self.link.read(self.headerBuf, self.headerBufLen)):
                return -1

            type = getPType(self.headerBuf)
            if (PDU_DISC == type):
                break
            elif (PDU_SYMM == type):
                if (not self.link.write(self.SYMM_PDU, len(self.SYMM_PDU))):
                    return -2
            else:
                return -3


        # Put DM PDU
        print("put a DM(Disconnect Mode) PDU to response the DISC PDU\n")
        # ssap = getDSAP(headerBuf)
        # dsap = getSSAP(headerBuf)
        self.headerBuf[0] = (self.dsap << 2) + (PDU_DM >> 2)
        self.headerBuf[1] = ((PDU_DM & 0x3) << 6) + self.ssap
        if (not self.link.write(self.headerBuf, 2)):
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
        if (2 > self.link.read(self.headerBuf, self.headerBufLen)):
            return -1
        type = getPType(self.headerBuf)
        if (PDU_SYMM != type):
            return -1

        # put a CONNECT PDU
        self.headerBuf[0] = (LLCP_DEFAULT_DSAP << 2) + (PDU_CONNECT >> 2)
        self.headerBuf[1] = ((PDU_CONNECT & 0x03) << 6) + LLCP_DEFAULT_SSAP
        body = "  urn:nfc:sn:snep"
        body[0] = 0x06
        body[1] = len(body) - 2 - 1
        if (self.link.write(self.headerBuf, 2, body, len(body) - 1)):
            return -2

        # wait for a CC PDU
        print("wait for a CC PDU\n")
        while 1:
            if (2 > self.link.read(self.headerBuf, self.headerBufLen)):
                return -1

            type = getPType(self.headerBuf)
            if (PDU_CC == type):
                break
            elif (PDU_SYMM == type):
                if (not self.link.write(self.SYMM_PDU, len(self.SYMM_PDU))):
                    return -2
            else:
                return -3

        return 1

    def disconnect(self, timeout: int) -> int:
        type = 0
    
        # try to get a SYMM PDU
        if (2 > self.link.read(self.headerBuf, self.headerBufLen)):
            return -1
        type = getPType(self.headerBuf)
        if (PDU_SYMM != type):
            return -1

        # put a DISC PDU
        self.headerBuf[0] = (LLCP_DEFAULT_DSAP << 2) + (PDU_DISC >> 2)
        self.headerBuf[1] = ((PDU_DISC & 0x03) << 6) + LLCP_DEFAULT_SSAP
        if (self.link.write(self.headerBuf, 2)):
            return -2

        # wait for a DM PDU
        print("wait for a DM PDU\n")
        while 1:
            if (2 > self.link.read(self.headerBuf, self.headerBufLen)):
                return -1

            type = getPType(self.headerBuf)
            if (PDU_CC == type):
                break
            elif (PDU_DM == type):
                if (self.link.write(self.SYMM_PDU, len(self.SYMM_PDU))):
                    return -2
            else:
                return -3

        return 1

    def write(self, header: str, hlen: int, body: str, blen: int) -> bool:
        type = 0
        buf = [0, 0, 0]
    
        if (self.mode):
            # Get a SYMM PDU
            if (2 != self.link.read(buf, len(buf))):
                return False

        if (self.headerBufLen < (hlen + 3)):
            return False

        for i in range(hlen).__reversed__():
            self.headerBuf[i + 3] = header[i]

        self.headerBuf[0] = (self.dsap << 2) + (PDU_I >> 2)
        self.headerBuf[1] = ((PDU_I & 0x3) << 6) + self.ssap
        self.headerBuf[2] = (self.ns << 4) + nr
        if (self.link.write(self.headerBuf, 3 + hlen, body, blen)):
            return False

        self.ns+=1
    
        # Get a RR PDU
        status = 0
        while 1:
            status = self.link.read(self.headerBuf, self.headerBufLen)
            if (2 > status):
                return False

            type = getPType(self.headerBuf)
            if (PDU_RR == type):
                break
            elif (PDU_SYMM == type):
                if (self.link.write(self.SYMM_PDU, len(self.SYMM_PDU))):
                    return False
            else:
                return False

        if (self.link.write(self., len(self.SYMM_PDU))):
            return False

        return True

    def read(self, buf: str, length: int) -> int:
        type = 0
        self.status = 0
    
        # Get INFO PDU
        while 1:
            status = self.link.read(buf, length)
            if (2 > status):
                return -1

            type = getPType(buf)
            if (PDU_I == type):
                break
            elif (PDU_SYMM == type):
                if (not self.link.write(self.SYMM_PDU, len(self.SYMM_PDU))):
                    return -2
            else:
                return -3

        blen = status - 3
        self.ssap = getDSAP(buf)
        self.dsap = getSSAP(buf)

        self.headerBuf[0] = (self.dsap << 2) + (PDU_RR >> 2)
        self.headerBuf[1] = ((PDU_RR & 0x3) << 6) + self.ssap
        self.headerBuf[2] = (buf[2] >> 4) + 1
        if (not self.link.write(self.headerBuf, 3)):
            return -2

        for i in range(blen):
            buf[i] = buf[i + 3]

        self.nr+=1
    
        return blen