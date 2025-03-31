from pn532pi.interfaces.pn532i2cBase import Pn532I2cBase, PN532_I2C_ADDRESS
from quick2wire.i2c import I2CMaster, writing, reading

class Pn532I2c(Pn532I2cBase):
    RPI_BUS0 = 0
    RPI_BUS1 = 1

    def __init__(self, bus: int):
        super().__init__()
        assert bus in [self.RPI_BUS0, self.RPI_BUS1], "Bus number must be 1 or 0"
        self._wire = None
        self._bus = bus

    def begin(self):
        self._wire = self.I2CMaster(self._bus)
        super().begin()

    def _write(self, data: bytes):
        self._wire.transaction(self.writing(PN532_I2C_ADDRESS, tuple(data)))
    
    def _read(self, num_bytes: int):
        responses = self._wire.transaction(self.reading(PN532_I2C_ADDRESS, num_bytes))
        return bytearray(responses[0])
