"""
    created by Jordan Gassaway, 1/5/2020
    Test for llcp class functions
"""
from unittest import TestCase, mock

from pn532pi.nfc.llcp import Llcp, buildHeader
from pn532pi.nfc.pn532 import Pn532


def _mock_link(resp_frames):
    """
    :param resp_frames: list of byte strings to return from read()
    """
    link = mock.MagicMock(spec=Pn532)
    link.tgGetData.side_effect = resp_frames
    link.tgSetData.return_value = True
    return link

def _get_header(interface):
    return interface.tgSetData.call_args[0][0]

def _get_body(interface):
    return interface.tgSetData.call_args[0][1]


class TestLlcp(TestCase):
    def test_buildHeader(self):
        """buildHeader correctly constructs an llcp header form the given variables"""
        tests_no_seq = [
            # dsap, ptype, ssap, header
            (1, 2, 3, b'\x04\x83'),
            (7, 5, 12, b'\x1d\x4c'),
            (21, 7, 24, b'\x55\xd8'),
            (33, 9, 17, b'\x86\x51'),
            (33, 9, 17, b'\x86\x51'),
            (1, 4, 32, b'\x05\x20'),
            (4, 4, 0x20, b'\x11\x20'),
        ]
        for test in tests_no_seq:
            dsap, ptype, ssap, exp_header = test
            header = buildHeader(dsap, ptype, ssap)
            self.assertEqual(exp_header, header,
                             'Incorrect llcp header. DSAP {:x}, PTYPE {:x}, SSAP {:x}'.format(dsap, ptype, ssap))

        tests_seq = [
            # dsap, ptype, ssap, header
            (1, 2, 3, 8, 13, b'\x04\x83\x8d'),
            (7, 5, 12, 5, 14, b'\x1d\x4c\x5e'),
            (21, 7, 24, 15, 7, b'\x55\xd8\xf7'),
        ]
        for test in tests_seq:
            dsap, ptype, ssap, ns, nr, exp_header = test
            header = buildHeader(dsap, ptype, ssap, ns, nr)
            self.assertEqual(exp_header, header,
                             'Incorrect llcp header. DSAP {:x}, PTYPE {:x}, SSAP {:x}'.format(dsap, ptype, ssap))

    def test_waitForConnection(self):
        """waitForConnection correctly writes a connect frame and outputs a CC frame"""
        frames = [
            (2, b'\x00\x00'),
            (2, b'\x00\x00'),
            (2, b'\x11\x03')
        ]
        link = _mock_link(resp_frames=frames)
        nfc = Llcp(link)

        status = nfc.waitForConnection()
        self.assertEqual(1, status, 'waitForConnection failed!')
        header = _get_header(link)
        self.assertEqual(b'\x0d\x84', header, 'Incorrect connection complete header')

    def test_waitForDisconnection(self):
        """waitForDisconnection correctly writes a disconnect frame and outputs a DM frame"""
        frames = [
            (2, b'\x00\x00'),
            (2, b'\x00\x00'),
            (2, b'\x11\x4d')
        ]
        link = _mock_link(resp_frames=frames)
        nfc = Llcp(link)

        status = nfc.waitForDisconnection()
        self.assertEqual(1, status, 'waitForDisconnection failed!')
        header = _get_header(link)
        self.assertEqual(b'\x01\xc0', header, 'Incorrect disconnected mode packet')

    def test_connect(self):
        """connect correctly writes a llcp connect frame"""
        frames = [
            (2, b'\x00\x00'),
            (2, b'\x01\x80')
        ]
        link = _mock_link(resp_frames=frames)
        nfc = Llcp(link)

        status = nfc.connect()
        self.assertEqual(1, status, 'connect failed!')
        header = _get_header(link)
        body = _get_body(link)
        self.assertEqual(b'\x11\x20', header)
        self.assertEqual(b'\x06\x0furn:nfc:sn:snep', body)

    def test_disconnect(self):
        """disconnect correctly writes an llcp disconnect frame"""
        frames = [
            (2, b'\x00\x00'),
            (2, b'\x11\xA0'),
        ]
        link = _mock_link(resp_frames=frames)
        nfc = Llcp(link)

        status = nfc.disconnect()
        self.assertEqual(1, status, 'disconnect failed!')
        header = _get_header(link)
        self.assertEqual(b'\x11\x60', header)

    def test_read(self):
        """read correctly parses an incoming llcp data frame and sends an RR packet"""
        frames = [
            (8, b'\x03\x00\x10data1'),
            (9, b'\x03\x00\x24data10'),
            (10, b'\x03\x00\x73data100'),
        ]
        link = _mock_link(resp_frames=frames)
        nfc = Llcp(link)

        for test in frames:
            length, packet = test
            num, data = nfc.read()
            self.assertEqual(length - 3, num, 'read failed or reported incorrect length')
            self.assertEqual(packet[3:], data, 'incorrect data returned')
            header = _get_header(link)
            nr = (packet[2] >> 4) + 1
            self.assertEqual(b'\x03\x40' + bytearray([nr]), header, 'Invalid read response')

    def test_write(self):
        """write correctly encapsulates the passed data in an llcp frame"""
        frames = [
            (2, b'\x03\x40'),
        ]
        link = _mock_link(resp_frames=frames)
        nfc = Llcp(link)

        status = nfc.write(bytearray(b'header'), bytearray(b'body'))
        self.assertTrue(status, 'write failed!')
        header = link.tgSetData.call_args_list[0][0][0]
        header_payload = bytearray(b'header')
        self.assertEqual(b'\x03\x00\x00' + header_payload, header, 'Invalid write header')
        body = link.tgSetData.call_args_list[0][0][1]
        self.assertEqual(b'body', body, 'Invalid write body')
