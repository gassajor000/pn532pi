"""
    created by Jordan Gassaway, 11/21/2019
    Test pn532spi class
"""
from unittest import TestCase
from PN532_SPI.pn532spi import pn532spi


class TestPn532spi(TestCase):
    def setUp(self):
        self.pn532 = pn532spi(ss=pn532spi.SS0_GPIO8)

    def test_write(self):
        self.fail()

    def test_read(self):
        self.fail()

    def test_begin(self):
        self.pn532.begin()

    def test_wakeup(self):
        self.fail('stuff')
        
    def test_writeCommand(self):
        self.fail()

    def test_readResponse(self):
        self.fail()

    def test_isReady(self):
        self.fail()

    def test_writeFrame(self):
        self.fail()

    def test_readAckFrame(self):
        self.fail()
