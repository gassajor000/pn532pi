"""
    created by Jordan Gassaway, 12/3/2019
    Test communication with PN532 over spi
"""
from unittest import TestCase
from pn532pi.interfaces.pn532spi import Pn532Spi

class TestPn532spiComm(TestCase):
    def setUp(self):
        self.pn532 = Pn532Spi(ss=Pn532Spi.SS0_GPIO8)
        self.pn532.begin()

    def test_getFirmware(self):
        self.pn532.writeCommand(bytearray([0x2]), bytearray())
        rsp = self.pn532.readResponse(10)
        print('Response {!r}'.format(rsp))
        self.assertEqual(bytearray([0x32, 0x1, 0x6, 0x7]), rsp[1])    # Check against known firmware ver
        self.assertEqual(4, rsp[0])    # Check length is correct
