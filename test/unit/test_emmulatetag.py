"""
    created by Jordan Gassaway, 1/8/2020
    Test for emulateTag class functions
"""
from unittest import TestCase, mock

from pn532pi.nfc.emulatetag import EmulateTag
from pn532pi.nfc.pn532 import Pn532


def _mock_pn532(resp_frames):
    """
    :param resp_frames: list of byte strings to return from tgGetData()
    """
    link = mock.MagicMock(spec=Pn532)
    link.return_value = link
    link.tgGetData.side_effect = resp_frames
    link.tgSetData.return_value = True
    link.SAMConfig.return_value = True
    link.tgInitAsTarget.return_value = 1
    return link


def _get_header(interface):
    return interface.tgSetData.call_args[0][0]


def _get_body(interface):
    return interface.tgSetData.call_args[0][1]


def do_emulate(nfc: EmulateTag):
    try:
        nfc.emulate()
    except StopIteration:   # Run out of frames to process
        pass


class TestEmulateTag(TestCase):
    def test_select_ndef_by_id(self):
        """ndef file can be selected by File ID"""
        frames = [
            (8, b'\x02\xA4\x00\x0c\x02\xe1\x04'),  # Select NDEF File
        ]
        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        do_emulate(nfc)
        header = _get_header(link)
        self.assertEqual(b'\x90\x00', header, 'Select operation failed!')
        self.assertEqual(2, nfc.currentFile, 'Incorrect file selected!')

    def test_select_compat_by_id(self):
        """compatibility container can be selected by file ID"""
        frames = [
            (8, b'\x02\xA4\x00\x0c\x02\xe1\x03'),  # Select Compatibility Container
        ]
        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        do_emulate(nfc)
        header = _get_header(link)
        self.assertEqual(b'\x90\x00', header, 'Select operation failed!')
        self.assertEqual(1, nfc.currentFile, 'Incorrect file selected!')

    def test_select_ndef_by_name(self):
        """ndef file can be selected by File Name"""
        frames = [
            (12, b'\x02\xA4\x04\x00\x07\xd2\x76\x00\x00\x85\x01\x01'),  # Select NDEF File
        ]
        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        do_emulate(nfc)

        header = _get_header(link)
        self.assertEqual(b'\x90\x00', header, 'Select operation failed!')
        self.assertEqual(2, nfc.currentFile, 'Incorrect file selected!')

    def test_read_ndef(self):
        """ndef file can be read"""
        frames = [
            (8, b'\x02\xA4\x00\x0c\x02\xe1\x04'),  # Select NDEF File
            (12, b'\x02\xB0\x00\x00\x2f'),    # Read Binary
        ]
        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        nfc.setNdefFile(b'\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8')
        do_emulate(nfc)

        header = _get_header(link)
        self.assertEqual(b'\x90\x00', header[-2:], 'Read operation failed!')
        self.assertEqual(b'\x00\x08\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8', header[:-2], 'Incorrect data read!')
        self.assertEqual(2, nfc.currentFile, 'Incorrect file selected!')

    def test_read_ndef_offset(self):
        """ndef file can be read from an offset in the file"""
        frames = [
            (8, b'\x02\xA4\x00\x0c\x02\xe1\x04'),  # Select NDEF File
            (12, b'\x02\xB0\x00\x03\x2f'),    # Read Binary
        ]
        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        nfc.setNdefFile(b'\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8')
        do_emulate(nfc)

        header = _get_header(link)
        self.assertEqual(b'\x90\x00', header[-2:], 'Read operation failed!')
        self.assertEqual(b'\xd2\xd3\xd4\xd5\xd6\xd7\xd8', header[:-2], 'Incorrect data read!')

    def test_read_compat(self):
        """compatibility container can be read"""
        frames = [
            (8, b'\x02\xA4\x00\x0c\x02\xe1\x03'),  # Select Compatibility Container
            (12, b'\x02\xB0\x00\x00\x2f'),    # Read Binary
        ]
        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        nfc.setNdefFile(b'\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8')
        do_emulate(nfc)

        header = _get_header(link)
        self.assertEqual(b'\x90\x00', header[-2:], 'Read operation failed!')
        self.assertEqual(b'\x00\x0F\x20\x00\x54\x00\xff\x04\x06\xe1\x04\x00\x80\x00\x00', header[:-2],
                         'Incorrect data read!')

    def test_read_compat_offset(self):
        """compatibility container can be read from an offset"""
        frames = [
            (8, b'\x02\xA4\x00\x0c\x02\xe1\x03'),  # Select Compatibility Container
            (12, b'\x02\xB0\x00\x04\x2f'),    # Read Binary
        ]
        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        nfc.setNdefFile(b'\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8')
        do_emulate(nfc)

        header = _get_header(link)
        self.assertEqual(b'\x90\x00', header[-2:], 'Read operation failed!')
        self.assertEqual(b'\x54\x00\xff\x04\x06\xe1\x04\x00\x80\x00\x00', header[:-2], 'Incorrect data read!')

    def test_update_binary(self):
        """ndef file can be written to by update binary"""
        frames = [
            (12, b'\x02\xD6\x00\x00\x06\x00\x08\xa1\xa2\xa3\xa4'),    # Update Binary
        ]
        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        nfc.setNdefFile(b'\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8')
        do_emulate(nfc)

        header = _get_header(link)
        self.assertEqual(b'\x90\x00', header, 'Update Binary operation failed!')
        self.assertEqual(b'\x00\x08\xa1\xa2\xa3\xa4\xd5\xd6\xd7\xd8', nfc.ndef_file, 'Incorrect data written!')

    def test_update_ndef_callback(self):
        """updateNdefCallback is called when binary is updated"""
        frames = [
            (12, b'\x02\xD6\x00\x00\x06\x00\x08\xa1\xa2\xa3\xa4'),    # Update Binary
        ]
        mock_callback = mock.MagicMock(name='callback')

        link = _mock_pn532(resp_frames=frames)
        nfc = EmulateTag(link)
        nfc.setNdefFile(b'\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8')
        nfc.updateNdefCallback = mock_callback
        do_emulate(nfc)

        mock_callback.assert_called_once_with(b'\xa1\xa2\xa3\xa4\xd5\xd6\xd7\xd8')