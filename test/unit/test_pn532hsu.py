"""
    created by Jordan Gassaway, 11/21/2019
    Test pn532hsu class
"""
from unittest import TestCase, mock


class MockUART(mock.Mock):
    """Mock for Serial interface"""
    read_buf = bytearray()
    write_buf = bytearray()
    def _get_data(self, num):
        out = self.read_buf[:num]
        if len(out) < num:
            out += bytearray([0 for i in range(num -  len(out))])
            self.read_buf = bytearray()
        else:
            self.read_buf = self.read_buf[num:]

        return out

    def read(self, num=0):
        self._mock_read(num)
        return self._get_data(num)

    def write(self, data):
        self._mock_write(data)
        self.write_buf += data
        return len(data)

MOCK_UART = MockUART(id='my mock_uart')

modules = {'serial': mock.MagicMock(Serial=mock.MagicMock(return_value=MOCK_UART)),
           'quick2wire.i2c': mock.MagicMock(), 'spidev': mock.MagicMock()}
with mock.patch.dict('sys.modules', modules):
    from pn532pi.interfaces.pn532hsu import Pn532Hsu

PN532_ACK = bytearray([0, 0, 0xFF, 0, 0xFF, 0])


class TestPn532hsu(TestCase):
    def test_begin(self):
        """pn532hsu.begin initializes with the correct parameters"""
        pn532 = Pn532Hsu(Pn532Hsu.RPI_MINI_UART)
        pn532.begin()

        modules['serial'].Serial.assert_called_once_with('/dev/serial0', baudrate=115200, timeout=100)  # Mini UART

    def test_wakeup(self):
        """pn532hsu.wakeup writes some data to the spi port"""
        pn532 = Pn532Hsu(Pn532Hsu.RPI_MINI_UART)
        pn532.begin()
        pn532.wakeup()  #  check bytes written/transfered
        self.assertTrue(MOCK_UART._mock_write.called, "write transaction not called")

    def test_writeCommand(self):
        """pn532hsu.writeCommand writes command frames correctly"""
        pn532 = Pn532Hsu(1)
        pn532.begin()

        frames = [  #  header, body, bytes written

            (bytearray([70, 80]), bytearray(), bytearray([0, 0, 255, 3, 253, 0xD4, 70, 80, 150, 0])),
            (bytearray([60]), bytearray([2, 3]), bytearray([0, 0, 255, 4, 252, 0xD4, 60, 2, 3, 235, 0])),
            (bytearray([50]), bytearray(), bytearray([0, 0, 255, 2, 254, 0xD4, 50, 250, 0])),
        ]
        for frame in frames:
            header, body, output = frame
            MOCK_UART.reset_mock()
            MOCK_UART.read_buf = PN532_ACK
            MOCK_UART.write_buf = bytearray()
            pn532.writeCommand(header=header, body=body)
            self.assertTrue(output in MOCK_UART.write_buf, 'Invalid data written')

    def test_invalid_ack(self):
        """writeCommand waits for an ack"""
        pn532 = Pn532Hsu(1)
        pn532.begin()

        # correct ack
        MOCK_UART.read_buf = PN532_ACK
        ret = pn532.writeCommand(header=bytearray([2]), body=bytearray())
        self.assertEqual(0, ret, "writeCommand failed!")

        # invalid ack
        MOCK_UART.read_buf = [1, 128, 128]
        ret = pn532.writeCommand(header=bytearray([2]), body=bytearray())
        self.assertEqual(-1, ret, "writeCommand succeeded with invalid ack!")

    def test_readResponse(self):
        """readResponse correctly parses a response frame"""
        pn532 = Pn532Hsu(1)
        pn532.begin()

        frames = [ # cmd    resp data    resp frame
            (bytearray([1]), bytearray([70, 80]), bytearray([0, 0, 255, 4, 252, 0xD5, 2, 70, 80, 147, 0])),
            (bytearray([2]), bytearray([60]), bytearray([0, 0, 255, 3, 253, 0xD5, 3, 60, 236, 0]))
        ]
        for frame in frames:
            cmd, resp_data, resp_frame = frame
            MOCK_UART.reset_mock()
            MOCK_UART.read_buf = PN532_ACK + resp_frame
            pn532.writeCommand(header=cmd, body=bytearray())

            length, resp = pn532.readResponse()
            self.assertGreaterEqual(length, 0, "readResponse failed!")
            self.assertEqual(len(resp), length, "length did not match response length")
            self.assertEqual(resp_data, resp, "Incorrect response")

    def test_invalid_length(self):
        """readResponse rejects frame with invalid length or invalid length checksum"""
        pn532 = Pn532Hsu(1)
        pn532.begin()

        # Bad length checksum
        cmd = bytearray([1])
        bad_len_checksum = bytearray([0, 0, 255, 4, 13, 0xD5, 2, 70, 80, 147, 0])
        bad_len = bytearray([0, 0, 255, 7, 252, 0xD5, 2, 70, 80, 147, 0])

        MOCK_UART.read_buf =  PN532_ACK + bad_len_checksum
        pn532.writeCommand(header=cmd, body=bytearray())
        length, resp = pn532.readResponse()
        self.assertGreaterEqual(length, -3, "readResponse did not return Invalid Frame")

        MOCK_UART.read_buf =  PN532_ACK + bad_len
        pn532.writeCommand(header=cmd, body=bytearray())
        length, resp = pn532.readResponse()
        self.assertGreaterEqual(length, -3, "readResponse did not return Invalid Frame")

    def test_invalid_preamble(self):
        """readResponse rejects frame with invalid preamble"""
        pn532 = Pn532Hsu(1)
        pn532.begin()

        # Bad length checksum
        cmd = bytearray([1])
        bad_preamble = bytearray([0, 2, 250, 4, 252, 0xD5, 2, 70, 80, 147, 0])

        MOCK_UART.read_buf = PN532_ACK + bad_preamble
        pn532.writeCommand(header=cmd, body=bytearray())
        length, resp = pn532.readResponse()
        self.assertGreaterEqual(length, -3, "readResponse did not return Invalid Frame")

    def test_invalid_checksum(self):
        """readResponse rejects frame with invalid checksum"""
        pn532 = Pn532Hsu(1)
        pn532.begin()

        # Bad length checksum
        cmd = bytearray([1])
        bad_checksum = bytearray([0, 0, 255, 4, 252, 0xD5, 2, 70, 80, 140, 0])

        MOCK_UART.read_buf = PN532_ACK + bad_checksum
        pn532.writeCommand(header=cmd, body=bytearray())
        length, resp = pn532.readResponse()
        self.assertGreaterEqual(length, -3, "readResponse did not return Invalid Frame")
