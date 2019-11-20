from PN532.pn532 import pn532


class macLink:
    def __init__(self, interface: pn532):
        self.pn532 = interface

    def activateAsTarget(self, timeout: int) -> int:
        self.pn532.begin()
        self.pn532.SAMConfig()
        return self.pn532.tgInitAsTarget(timeout)

    def  getHeaderBuffer(self) -> (str, int):
        return self.pn532.getBuffer(len)

    def write(self, header: str, hlen: int, body: str, blen: int) -> bool:
        return self.pn532.tgSetData(header, hlen, body, blen)

    def read(self, buf: str, blen: int) -> int:
        return self.pn532.tgGetData(buf, blen)
