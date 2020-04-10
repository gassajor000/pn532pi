"""
    created by Jordan Gassaway, 12/6/2019
    Test pn532 functions
"""
from unittest import TestCase
from pn532pi.interfaces.pn532i2c import Pn532I2c
from pn532pi.nfc.pn532 import Pn532

class TestPn532Func(TestCase):
    def setUp(self):
        # self.interface = pn532spi(pn532spi.SS0_GPIO8)
        self.interface = Pn532I2c(1)
        self.interface.begin()
        self.pn532 = Pn532(self.interface)

    def test_getFirmware(self):
        fw_ver = self.pn532.getFirmwareVersion()
        self.assertEqual(fw_ver, 0x32010607, 'Invalid fw version returned')

    def test_SAMConfig(self):
        ret = self.pn532.SAMConfig()
        self.assertTrue(ret)

    def test_readGPIO(self):
        gpio = self.pn532.readGPIO()
        print("gpio: {:#x}".format(gpio))