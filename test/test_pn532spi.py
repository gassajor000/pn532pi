"""
    created by Jordan Gassaway, 11/21/2019
    Test pn532spi class
"""
from unittest import TestCase, mock

class MockSpi(mock.Mock):
    """Mock for SpiDev interface"""
    read_buf = []
    write_buf = []
    def _get_data(self, num):
        out = self.read_buf[:num]
        if len(out) < num:
            out += [0 for i in range(num -  len(out))]
            self.read_buf = []
        else:
            self.read_buf = self.read_buf[num:]

        return out

    def readbytes(self, num):
        self._mock_readbytes(num)
        return self._get_data(num)

    def writebytes(self, data):
        self._mock_writebytes(data)
        self.write_buf += data
        return len(data)

    def xfer2(self, data):
        self._mock_xfer2(data)
        self.write_buf += data
        return self._get_data(len(data))

MOCK_SPI = MockSpi(id='my mock_spi')

modules = {'spidev': mock.MagicMock(SpiDev=mock.MagicMock(return_value=MOCK_SPI))}
with mock.patch.dict('sys.modules', modules):
    from PN532_SPI.pn532spi import pn532spi

PN532_ACK = [0, 0, 0xFF, 0, 0xFF, 0]

class TestPn532spi(TestCase):
    def test_begin(self):
        """pn532spi.begin initializes with the correct parameters"""
        pn532 = pn532spi(ss=pn532spi.SS0_GPIO8)
        pn532.begin()

        self.assertEqual(0, MOCK_SPI.mode, "spi mode not set to 0!")
        self.assertEqual(False, MOCK_SPI.cshigh, "spi cshigh not set to False!")
        self.assertLessEqual(5000000, MOCK_SPI.max_speed_hz, "spi max_speed_hz greater than 5MHz!")
        MOCK_SPI.open.assert_called_once_with(0, 0)     # SPI Bus 0, SS 0

        MOCK_SPI.reset_mock()
        pn532 = pn532spi(ss=pn532spi.SS1_GPIO7)
        pn532.begin()

        MOCK_SPI.open.assert_called_once_with(0, 1)  # SPI Bus 0, SS 1

    def test_invalidSlaveSelect(self):
        """pn532spi accepts only valid slave select values"""
        pn532spi(ss=0)
        pn532spi(ss=1)

        with self.assertRaises(AssertionError):
            pn532spi(ss=3)

        with self.assertRaises(AssertionError):
            pn532spi(ss='invalid ss')

    def test_wakeup(self):
        """pn532spi.wakeup writes some data to the spi port"""
        pn532 = pn532spi(ss=pn532spi.SS0_GPIO8)
        pn532.wakeup()  #  check bytes written/transfered
        self.assertTrue(MOCK_SPI._mock_writebytes.called or MOCK_SPI._mock_xfer2.called, "writebytes or xfer2 not called")

    def test_writeCommand(self):
        """pn532spi.writeCommand writes command frames correctly"""
        pn532 = pn532spi(0)
        rev_b = {'01': 128, '02': 64, '03': 192,  '04': 32, 'D4': 43, '70': 98, '80': 10, '60': 60, '50': 76,
                 '~02': 127, '~03': 191, '~04': 63, 'c7080': 105, 'c6023': 215, 'c50': 95}
        frames = [  #  header, body, bytes written
            (bytearray([70, 80]), bytearray(), [rev_b['01'], 0, 0, 255, rev_b['03'], rev_b['~03'], rev_b['D4'], rev_b['70'], rev_b['80'], rev_b['c7080'], 0]),
            (bytearray([60]), bytearray([2, 3]), [rev_b['01'], 0, 0, 255, rev_b['04'], rev_b['~04'], rev_b['D4'], rev_b['60'], rev_b['02'], rev_b['03'], rev_b['c6023'], 0]),
            (bytearray([50]), bytearray(), [rev_b['01'], 0, 0, 255, rev_b['02'], rev_b['~02'], rev_b['D4'], rev_b['50'], rev_b['c50'], 0]),
        ]
        for frame in frames:
            header, body, output = frame
            MOCK_SPI.reset_mock()
            MOCK_SPI.read_buf = [0] + PN532_ACK
            pn532.writeCommand(header=header, body=body)
            MOCK_SPI._mock_writebytes.assert_called_once_with(output)


    def test_invalid_ack(self):
        """writeCommand waits for an ack"""
        pass

    def test_wait_for_ready(self):
        """writeCommand waits for a status of 1"""
        pass

    def test_readResponse(self):
        """readResponse correctly parses a response frame"""
        pass