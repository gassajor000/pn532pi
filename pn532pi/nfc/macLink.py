from pn532pi.nfc.pn532 import Pn532


class MacLink:
    def __init__(self, interface: Pn532):
        self.pn532 = interface

    def activateAsTarget(self, timeout: int) -> int:
        self.pn532.SAMConfig()
        return self.pn532.tgInitAsTargetP2P(timeout)

    def write(self, header: bytearray, body: bytearray = bytearray()) -> bool:
        return self.pn532.tgSetData(header, body)

    def read(self) -> (int, bytearray):
        return self.pn532.tgGetData()
