from pn532pi.pn532.pn532 import pn532


class macLink:
    def __init__(self, interface: pn532):
        self.pn532 = interface

    def activateAsTarget(self, timeout: int) -> int:
        self.pn532.SAMConfig()
        return self.pn532.tgInitAsTargetP2P(timeout)

    def write(self, header: bytearray, body: bytearray = bytearray()) -> bool:
        return self.pn532.tgSetData(header, body)

    def read(self) -> (int, bytearray):
        return self.pn532.tgGetData()
