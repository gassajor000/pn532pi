"""
    created by Jordan Gassaway, 1/5/2020
    Test for snep class functions
"""
from unittest import TestCase, mock

from pn532pi.nfc.llcp import Llcp
from pn532pi.nfc.snep import Snep


def _mock_llcp(resp_frames):
    """
    :param resp_frames: list of byte strings to return from read()
    """
    link = mock.MagicMock(spec=Llcp)
    link.return_value = link
    link.read.side_effect = resp_frames
    link.write.return_value = True
    link.activate.return_value = 1
    link.connect.return_value = 1
    link.waitForConnection.return_value = 1
    return link

def _get_header(interface):
    return interface.write.call_args[0][0]

def _get_body(interface):
    return interface.write.call_args[0][1]


class TestSnep(TestCase):
    def test_read(self):
        """read correctly interprets a snep packet"""
        frames = [
            (11, b'\x10\x02\x00\x00\x00\x05data1'),
            (12, b'\x10\x02\x00\x00\x00\x06data10'),
            (13, b'\x10\x02\x00\x00\x00\x07data100'),
        ]
        link = _mock_llcp(resp_frames=frames)
        with mock.patch('pn532pi.nfc.snep.Llcp', new=link):
            nfc = Snep(link)

            for test in frames:
                length, packet = test
                num, data = nfc.read()
                self.assertEqual(length - 6, num, 'read failed or reported incorrect length')
                self.assertEqual(packet[6:], data, 'incorrect data returned')
                header = _get_header(link)
                self.assertEqual(b'\x10\x81\x00\x00\x00\x00', header, 'Invalid read response')

    def test_write(self):
        """write correctly encapsulates data in a snep packet"""
        frames = [
            (6, b'\x10\x81abcd'),
        ]
        link = _mock_llcp(resp_frames=frames)
        with mock.patch('pn532pi.nfc.snep.Llcp', new=link):
            nfc = Snep(link)

            status = nfc.write(bytearray(b'data'))
            self.assertEqual(1, status, 'write failed!')
            header = _get_header(link)
            self.assertEqual(b'\x10\x02\x00\x00\x00\x04', header, 'Invalid write header')
            body = _get_body(link)
            self.assertEqual(b'data', body, 'Invalid write body')
