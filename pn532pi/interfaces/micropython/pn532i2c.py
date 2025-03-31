from pn532pi.interfaces.pn532i2cBase import Pn532I2cBase, PN532_I2C_ADDRESS
import machine

class Pn532I2c(Pn532I2cBase):
    def __init__(self, scl_pin: int, sda_pin: int):
        """
        Initialize the PN532 I2C interface using MicroPython's machine.I2C.

        Args:
            scl_pin (int): GPIO pin for I2C SCL.
            sda_pin (int): GPIO pin for I2C SDA.
            freq (int): I2C frequency (default: 100kHz).
        """
        super().__init__()
        self._i2c = machine.I2C(0, scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))        

    def _write(self, data: bytes):
        self._i2c.writeto(PN532_I2C_ADDRESS, data)
    
    def _read(self, num_bytes: int):
        return self._i2c.readfrom(PN532_I2C_ADDRESS, num_bytes)