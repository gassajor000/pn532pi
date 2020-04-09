"""
    created by Jordan Gassaway, 11/21/2019
    Test pn532i2c class
"""
from unittest import TestCase, mock


def mock_reading(addr, num):
    return ('read', addr, num)


def mock_writing(addr, data):
    return ('write', addr, list(data))


class MockI2C(mock.Mock):
    """Mock for quick2wire interface"""
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

    def transaction(self, transaction):
        self._mock_transaction(transaction)
        op, addr, data = transaction

        assert addr == 0x24, "Invalid address {:x}".format(addr)
        assert op in ['read', 'write'], 'invalid op'

        if op == 'write':
            self._write_bytes(data)
            print('write_bytes', data)
            self.write_buf += data
            return []

        if op == 'read':
            self._read_bytes(data)
            print('read_bytes', data)
            return [self._get_data(data)]

MOCK_I2C = MockI2C(id='my mock_i2c')

modules = {'quick2wire.i2c': mock.MagicMock(I2CMaster=mock.MagicMock(return_value=MOCK_I2C), reading=mock_reading,
                                            writing=mock_writing),
           'serial': mock.MagicMock(), 'spidev': mock.MagicMock()}
with mock.patch.dict('sys.modules', modules):
    from pn532pi.interfaces.pn532i2c import Pn532I2c

PN532_ACK = [0, 0, 0xFF, 0, 0xFF, 0]


class TestPn532i2c(TestCase):
    def test_begin(self):
        """pn532i2c.begin initializes with the correct parameters"""
        pn532 = Pn532I2c(bus=Pn532I2c.RPI_BUS1)
        pn532.begin()

        modules['quick2wire.i2c'].I2CMaster.assert_called_once_with(1)  # I2C Bus 1

    def test_wakeup(self):
        """pn532i2c.wakeup writes some data to the spi port"""
        pn532 = Pn532I2c(bus=Pn532I2c.RPI_BUS1)
        pn532.begin()
        pn532.wakeup()  #  check bytes written/transfered
        self.assertTrue(MOCK_I2C._write_bytes.called, "write transaction not called")

    def test_writeCommand(self):
        """pn532i2c.writeCommand writes command frames correctly"""
        pn532 = Pn532I2c(1)
        pn532.begin()

        frames = [  #  header, body, bytes written

            (bytearray([70, 80]), bytearray(), [0, 0, 255, 3, 253, 0xD4, 70, 80, 150, 0]),
            (bytearray([60]), bytearray([2, 3]), [0, 0, 255, 4, 252, 0xD4, 60, 2, 3, 235, 0]),
            (bytearray([50]), bytearray(), [0, 0, 255, 2, 254, 0xD4, 50, 250, 0]),
        ]
        for frame in frames:
            header, body, output = frame
            MOCK_I2C.reset_mock()
            MOCK_I2C.read_buf = [1] + PN532_ACK  # Ready bit
            pn532.writeCommand(header=header, body=body)
            MOCK_I2C._write_bytes.assert_called_once_with(output)

    def test_invalid_ack(self):
        """writeCommand waits for an ack"""
        pn532 = Pn532I2c(1)
        pn532.begin()

        # correct ack
        MOCK_I2C.read_buf = [1] + PN532_ACK
        ret = pn532.writeCommand(header=bytearray([2]), body=bytearray())
        self.assertEqual(0, ret, "writeCommand failed!")

        # invalid ack
        MOCK_I2C.read_buf = [1, 128, 128]
        ret = pn532.writeCommand(header=bytearray([2]), body=bytearray())
        self.assertEqual(-1, ret, "writeCommand succeeded with invalid ack!")

    def test_wait_for_ready(self):
        """writeCommand waits for a status of 1 before reading ack"""
        pn532 = Pn532I2c(1)
        pn532.begin()

        # no ready/ack
        ret = pn532.writeCommand(header=bytearray([2]), body=bytearray())
        self.assertEqual(-2, ret, "writeCommand did not timeout waiting for ack!")

        # ready + ack
        MOCK_I2C.read_buf = [1] + PN532_ACK
        ret = pn532.writeCommand(header=bytearray([2]), body=bytearray())
        self.assertEqual(0, ret, "writeCommand failed!")

    def test_readResponse(self):
        """readResponse correctly parses a response frame"""
        pn532 = Pn532I2c(1)
        pn532.begin()

        frames = [ # cmd    resp data    resp frame
            (bytearray([1]), bytearray([70, 80]), [0, 0, 255, 4, 252, 0xD5, 2, 70, 80, 147, 0]),
            (bytearray([2]), bytearray([60]), [0, 0, 255, 3, 253, 0xD5, 3, 60, 236, 0])
        ]
        for frame in frames:
            cmd, resp_data, resp_frame = frame
            MOCK_I2C.reset_mock()
            MOCK_I2C.read_buf = [1] + PN532_ACK + [1] + resp_frame[:5] + [1] + resp_frame
            pn532.writeCommand(header=cmd, body=bytearray())

            length, resp = pn532.readResponse()
            self.assertGreaterEqual(length, 0, "readResponse failed!")
            self.assertEqual(len(resp), length, "length did not match response length")
            self.assertEqual(resp_data, resp, "Incorrect response")

    def test_invalid_length(self):
        """readResponse rejects frame with invalid length or invalid length checksum"""
        pn532 = Pn532I2c(1)
        pn532.begin()

        # Bad length checksum
        cmd = bytearray([1])
        bad_len_checksum = [0, 0, 255, 4, 13, 0xD5, 2, 70, 80, 147, 0]
        bad_len = [0, 0, 255, 7, 252, 0xD5, 2, 70, 80, 147, 0]

        MOCK_I2C.read_buf = [1] + PN532_ACK + [1] + bad_len_checksum[:5] + [1] + bad_len_checksum
        pn532.writeCommand(header=cmd, body=bytearray())
        length, resp = pn532.readResponse()
        self.assertGreaterEqual(length, -3, "readResponse did not return Invalid Frame")

        MOCK_I2C.read_buf = [1] + PN532_ACK + [1] + bad_len[:5] + [1] + bad_len
        pn532.writeCommand(header=cmd, body=bytearray())
        length, resp = pn532.readResponse()
        self.assertGreaterEqual(length, -3, "readResponse did not return Invalid Frame")

    def test_invalid_preamble(self):
        """readResponse rejects frame with invalid preamble"""
        pn532 = Pn532I2c(1)
        pn532.begin()

        # Bad length checksum
        cmd = bytearray([1])
        bad_preamble = [0, 2, 250, 4, 252, 0xD5, 2, 70, 80, 147, 0]

        MOCK_I2C.read_buf = [1] + PN532_ACK + [1] + bad_preamble[:5] + [1] + bad_preamble
        pn532.writeCommand(header=cmd, body=bytearray())
        length, resp = pn532.readResponse()
        self.assertGreaterEqual(length, -3, "readResponse did not return Invalid Frame")

    def test_invalid_checksum(self):
        """readResponse rejects frame with invalid checksum"""
        pn532 = Pn532I2c(1)
        pn532.begin()

        # Bad length checksum
        cmd = bytearray([1])
        bad_checksum = [0, 0, 255, 4, 252, 0xD5, 2, 70, 80, 140, 0]

        MOCK_I2C.read_buf = [1] + PN532_ACK + [1] + bad_checksum[:5] + [1] + bad_checksum
        pn532.writeCommand(header=cmd, body=bytearray())
        length, resp = pn532.readResponse()
        self.assertGreaterEqual(length, -3, "readResponse did not return Invalid Frame")
