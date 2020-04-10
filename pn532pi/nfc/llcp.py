from pn532pi.nfc.macLink import MacLink
from pn532pi.nfc.pn532 import Pn532

# LLCP PDU Type Values
from pn532pi.nfc.pn532_log import DMSG

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


def buildHeader(dsap, ptype, ssap, ns = None, nr = None):
    """Assembles an llcp header
    Required
    bits 0-5 SSAP
    bits 6-9 PTYPE
    bits 10-15 DSAP
    Optional sequence bits
    bits 0-3 NS
    bits 4-7 NR
    """
    req_header = ((dsap & 0x3f) << 10) | ((ptype & 0x0f) << 6) | (ssap & 0x3f)
    req_header_bytes = [(req_header >> 8) & 0xff, req_header & 0xff]
    if ns is None or nr is None:
        return bytearray(req_header_bytes)
    else:
        seq_bits = ((ns & 0xf) << 4) | (nr & 0xf)
        return bytearray(req_header_bytes + [seq_bits])

def getPType(buf) -> int:
    return ((buf[0] & 0x3) << 2) + (buf[1] >> 6)


def getSSAP(buf):
    return buf[1] & 0x3f


def getDSAP(buf):
    return buf[0] >> 2

class Llcp:
    SYMM_PDU = [0, 0]

    def __init__(self, interface: Pn532):
        self.link = MacLink(interface)
        self.ns = 0
        self.nr = 0
        self.mode = 0
        self.dsap = 0
        self.ssap = 0

    def activate(self, timeout: int = 0):
        return self.link.activateAsTarget(timeout)
    
    def waitForConnection(self, timeout: int = LLCP_DEFAULT_TIMEOUT) -> int:
        type = 0
    
        self.mode = 1
        self.ns = 0
        self.nr = 0
    
        # Get CONNECT PDU
        DMSG("wait for a CONNECT PDU\n")
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
        DMSG("put a CC(Connection Complete) PDU to response the CONNECT PDU\n")
        ssap = getDSAP(data)
        dsap = getSSAP(data)
        header = buildHeader(dsap, PDU_CC, ssap)
        if (not self.link.write(header)):
            return -2

        return 1

    def waitForDisconnection(self, timeout: int = LLCP_DEFAULT_TIMEOUT) -> int:
        type = 0
    
        # Get DISC PDU
        DMSG("wait for a DISC PDU\n")
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
        DMSG("put a DM(Disconnect Mode) PDU to response the DISC PDU\n")
        # ssap = getDSAP(headerBuf)
        # dsap = getSSAP(headerBuf)
        header = buildHeader(self.dsap, PDU_DM, self.ssap)
        if (not self.link.write(header)):
            return -2

        return 1

    def connect(self, timeout: int = LLCP_DEFAULT_TIMEOUT) -> int:
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
        header = buildHeader(LLCP_DEFAULT_DSAP, PDU_CONNECT, LLCP_DEFAULT_SSAP)
        body = bytearray(b"  urn:nfc:sn:snep")
        body[0] = 0x06
        body[1] = len(body) - 2
        if (not self.link.write(header, body)):
            return -2

        # wait for a CC PDU
        DMSG("wait for a CC PDU\n")
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

    def disconnect(self, timeout: int = LLCP_DEFAULT_TIMEOUT) -> int:
        type = 0
    
        # try to get a SYMM PDU
        status, data = self.link.read()
        if (2 > status):
            return -1
        type = getPType(data)
        if (PDU_SYMM != type):
            return -1

        # put a DISC PDU
        header = buildHeader(LLCP_DEFAULT_DSAP, PDU_DISC, LLCP_DEFAULT_SSAP)
        if (not self.link.write(header)):
            return -2

        # wait for a DM PDU
        DMSG("wait for a DM PDU\n")
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

        full_header = buildHeader(self.dsap, PDU_I, self.ssap, self.ns, self.nr) + header

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

        header = buildHeader(self.dsap, PDU_RR, self.ssap)
        header.append((data[2] >> 4) + 1)   # ns = 0, nr = ns of packet + 1

        if (not self.link.write(header)):
            return -2, bytearray()

        self.nr += 1
    
        return (blen, data[3:])