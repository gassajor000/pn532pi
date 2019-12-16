"""
    created by Jordan Gassaway, 12/6/2019
    Test pn532 functions
"""
from unittest import TestCase, mock
from PN532.pn532 import pn532
from PN532.pn532Interface import pn532Interface


def _mock_interface(resp_frames):
    """
    :param resp_frames: list of frames to return from calls readResponse (status, frame)
    """
    interface = mock.MagicMock(spec=pn532Interface)
    interface.readResponse.side_effect = resp_frames
    interface.writeCommand.return_value = 0
    return interface


def _get_header(interface, call=0):
    return interface.writeCommand.call_args[call][0]


def _get_body(interface, call=0):
    return interface.writeCommand.call_args[call][1]


class TestPn532(TestCase):
    def test_getFirmware(self):
        """getFirmware correctly queries firmware and parses response"""
        frames = [
            (0, b'\x01\x02\x03\x04')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = pn532(interface)
        fw_ver = nfc.getFirmwareVersion()
        self.assertEqual(fw_ver, 0x1020304, 'Incorrect firmware version returned')
        interface.writeCommand.assert_called_with(b'\x02')

    def test_SAMConfig(self):
        """getFirmware correctly queries gpio and parses response"""
        frames = [
            (0, bytearray())
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = pn532(interface)

        ret = nfc.SAMConfig()
        self.assertTrue(ret, 'SAMConfig failed')
        self.assertTrue(interface.writeCommand.called)

        header = _get_header(interface)
        pattern =  b'\x14\x01.\x01'  # SAM config CMD, Normal mode, timeout, use IRQ
        self.assertRegex(header, pattern, 'Incorrect SAMConfig command')

    def test_readGPIO(self):
        """readGPIO correctly queries gpio and parses response"""
        frames = [
            (0, b'\xab\x02\x03')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = pn532(interface)

        gpio = nfc.readGPIO()
        self.assertEqual(gpio, 0xab, 'Incorrect gpio data returned')
        interface.writeCommand.assert_called_once_with(b'\x0C')

    def test_writeGPIO(self):
        """writeGPIO correctly writes gpio and parses response"""
        frames = [
            (0, bytearray())
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = pn532(interface)

        result = nfc.writeGPIO(0xcd)
        self.assertTrue(result, 'writeGPIO failed!')
        interface.writeCommand.assert_called_once_with(b'\x0e\xdd\x00')      # write GPIO CMD, P3 | valid, P7

    def test_readRegister(self):
        """readRegister correctly queries gpio and parses response"""
        frames = [
            (0, b'\xab')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = pn532(interface)

        data = nfc.readRegister(3)
        self.assertEqual(data, 0xab, 'Incorrect register data returned')
        interface.writeCommand.assert_called_once_with(b'\x06\x00\x03')  # read reg CMD, reg high, reg low

    def test_writeRegister(self):
        """writeRegister correctly writes gpio and parses response"""
        frames = [
            (0, bytearray())
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = pn532(interface)

        result = nfc.writeRegister(0xabcd, 0x22)
        self.assertTrue(result, 'writeRegister failed!')
        interface.writeCommand.assert_called_once_with(b'\x08\xab\xcd\x22')  # write reg CMD, reg high, reg low, val

    def test_inDataExchange(self):
        """inDataExchange correctly executes a data exchange"""
        frames = [
            (0, b'\x00\x01\x02\x03\x04')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = pn532(interface)

        status, data = nfc.inDataExchange(b'\x0a\x0b\x0c\x0d')
        self.assertTrue(status, 'inDataExchange failed!')
        self.assertEqual(data, b'\x01\x02\x03\x04')

        header = _get_header(interface)
        body = _get_body(interface)
        self.assertRegex(header, b'\x40\x00', 'Incorrect inDataExchange command')
        self.assertRegex(body, b'\x0a\x0b\x0c\x0d', 'Incorrect inDataExchange command')
