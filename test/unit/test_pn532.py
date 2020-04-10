"""
    created by Jordan Gassaway, 12/6/2019
    Test pn532 functions
"""
import re
from unittest import TestCase, mock
from pn532pi.nfc.pn532 import Pn532
from pn532pi.interfaces.pn532Interface import Pn532Interface


def _mock_interface(resp_frames):
    """
    :param resp_frames: list of frames to return from calls readResponse (status, frame)
    """
    interface = mock.MagicMock(spec=Pn532Interface)
    interface.readResponse.side_effect = resp_frames
    interface.writeCommand.return_value = 0
    return interface


def _get_header(interface):
    return interface.writeCommand.call_args[0][0]


def _get_body(interface, call=0):
    return interface.writeCommand.call_args[call][1]


class TestPn532(TestCase):
    def test_getFirmware(self):
        """getFirmware correctly queries firmware and parses response"""
        frames = [
            (0, b'\x01\x02\x03\x04')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)
        fw_ver = nfc.getFirmwareVersion()
        self.assertEqual(fw_ver, 0x1020304, 'Incorrect firmware version returned')
        interface.writeCommand.assert_called_with(b'\x02')

    def test_SAMConfig(self):
        """getFirmware correctly queries gpio and parses response"""
        frames = [
            (0, bytearray())
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        ret = nfc.SAMConfig()
        self.assertTrue(ret, 'SAMConfig failed')
        self.assertTrue(interface.writeCommand.called)

        header = _get_header(interface)
        pattern = b'\x14\x01.\x01'  # SAM config CMD, Normal mode, timeout, use IRQ
        self.assertRegex(header, pattern, 'Incorrect SAMConfig command')

    def test_readGPIO(self):
        """readGPIO correctly queries gpio and parses response"""
        frames = [
            (0, b'\xab\x02\x03')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        gpio = nfc.readGPIO()
        self.assertEqual(gpio, 0xab, 'Incorrect gpio data returned')
        interface.writeCommand.assert_called_once_with(b'\x0C')

    def test_writeGPIO(self):
        """writeGPIO correctly writes gpio and parses response"""
        frames = [
            (0, bytearray())
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        result = nfc.writeGPIO(0xcd)
        self.assertTrue(result, 'writeGPIO failed!')
        interface.writeCommand.assert_called_once_with(b'\x0e\xdd\x00')  # write GPIO CMD, P3 | valid, P7

    def test_readRegister(self):
        """readRegister correctly queries gpio and parses response"""
        frames = [
            (0, b'\xab')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        data = nfc.readRegister(3)
        self.assertEqual(data, 0xab, 'Incorrect register data returned')
        interface.writeCommand.assert_called_once_with(b'\x06\x00\x03')  # read reg CMD, reg high, reg low

    def test_writeRegister(self):
        """writeRegister correctly writes gpio and parses response"""
        frames = [
            (0, bytearray())
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        result = nfc.writeRegister(0xabcd, 0x22)
        self.assertTrue(result, 'writeRegister failed!')
        interface.writeCommand.assert_called_once_with(b'\x08\xab\xcd\x22')  # write reg CMD, reg high, reg low, val

    def test_inDataExchange(self):
        """inDataExchange correctly executes a data exchange"""
        frames = [
            (0, b'\x00\x01\x02\x03\x04')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status, data = nfc.inDataExchange(b'\x0a\x0b\x0c\x0d')
        self.assertTrue(status, 'inDataExchange failed!')
        self.assertEqual(data, b'\x01\x02\x03\x04')

        header = _get_header(interface)
        body = _get_body(interface)
        self.assertRegex(header, b'\x40\x00', 'Incorrect inDataExchange command')
        self.assertRegex(body, b'\x0a\x0b\x0c\x0d', 'Incorrect inDataExchange command')

    def test_inRelease(self):
        """inRelease correctly executes a data exchange"""
        frames = [
            (0, b'\x00')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status = nfc.inRelease(relevantTarget=0x3)
        self.assertTrue(status, 'inRelease failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x52\x03', header, 'Incorrect inRelease command')

    def test_readPassiveTargetID(self):
        """readPassiveTargetID correctly executes read passive target ID command"""
        frames = [
            (0, b'\x01\x07\x02\x03\x04\x02\xaa\xbb')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status, data = nfc.readPassiveTargetID(cardbaudrate=0, inlist=True)
        self.assertTrue(status, 'readPassiveTargetID failed!')
        self.assertEqual(data, b'\xaa\xbb', 'Incorrect uid returned')
        self.assertEqual(nfc.inListedTag, 0x7, 'Tag was not inlisted')

        header = _get_header(interface)
        self.assertRegex(header, b'\x4A[\x00-\x02]\x00', 'Incorrect inDataExchange command')

    def test_setRFField(self):
        """setRFField correctly sets the RF on/ff and autoRFCA fields"""
        frames = [
            (0, b''),
            (0, b'')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status = nfc.setRFField(autoRFCA=True, RFOn=True)
        self.assertTrue(status, 'setRFField failed!')

        header = _get_header(interface)
        self.assertRegex(header, b'\x32\x01\x03', 'Incorrect setRFField command')
        status = nfc.setRFField(autoRFCA=True, RFOn=False)
        self.assertTrue(status, 'setRFField failed!')

        header = _get_header(interface)
        self.assertRegex(header, b'\x32\x01\x02', 'Incorrect setRFField command')

    def test_tgSetData(self):
        """tgSetData correctly writes data"""
        frames = [
            (0, b'\x00'),
            (0, b'\x02')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status = nfc.tgSetData(header=b'\x01\x02', body=b'\xaa\xbb')
        self.assertTrue(status, 'tgSetData failed!')

        header = _get_header(interface)
        body = _get_body(interface)
        self.assertRegex(header, b'\x8E\01\x02', 'Incorrect tgSetData command')
        self.assertRegex(body, b'\xaa\xbb', 'Incorrect tgSetData command')

        status = nfc.tgSetData(header=b'\x01\x02', body=b'\xaa\xbb')
        self.assertFalse(status, 'tgSetData succeeded when it should have failed!')

    def test_tgGetData(self):
        """tgGetData correctly reads data"""
        frames = [
            (6, b'\x00abcde'),
            (6, b'\x02abcde'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status, data = nfc.tgGetData()
        self.assertEqual(5, status, 'tgGetData failed!')
        self.assertEqual(b'abcde', data, 'Invalid data returned')

        header = _get_header(interface)
        self.assertRegex(header, b'\x86', 'Incorrect tgGetData command')

        status, _ = nfc.tgGetData()
        self.assertEqual(-5, status, 'tgGetData failed!')

    def test_mifareclassic_AuthenticateBlock(self):
        """mifareclassic_AuthenticateBlock correctly authenticates a block"""
        frames = [
            (0, b'\x00'),
            (0, b'\x00')
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)
        uid = b'\x0a\x0b\x0c\x0d'
        key = b'\xff\xfe\xfd\xfc\xfb\xfa'

        status = nfc.mifareclassic_AuthenticateBlock(uid=uid, blockNumber=0x12, keyNumber=0, keyData=key)
        self.assertTrue(status, 'mifareclassic_AuthenticateBlock failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x40\x01\x60\x12' + key + uid, header, 'Incorrect mifareclassic_AuthenticateBlock command')

        status = nfc.mifareclassic_AuthenticateBlock(uid=uid, blockNumber=0x12, keyNumber=1, keyData=key)
        self.assertTrue(status, 'mifareclassic_AuthenticateBlock failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x40\x01\x61\x12' + key + uid, header, 'Incorrect mifareclassic_AuthenticateBlock command')

    def test_mifareclassic_ReadDataBlock(self):
        """mifareclassic_ReadDataBlock correctly reads a data block"""
        frames = [
            (0, b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status, data = nfc.mifareclassic_ReadDataBlock(blockNumber=0x12)
        self.assertTrue(status, 'mifareclassic_ReadDataBlock failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x40\x01\x30\x12', header, 'Incorrect mifareclassic_ReadDataBlock command')
        self.assertEqual(b'\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18', data,
                         'Incorrect data returned')

    def test_mifareclassic_WriteDataBlock(self):
        """mifareclassic_WriteDataBlock correctly reads a data block"""
        frames = [
            (0, b'\x00'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status= nfc.mifareclassic_WriteDataBlock(blockNumber=0x12, data=b'\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18')
        self.assertTrue(status, 'mifareclassic_WriteDataBlock failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x40\x01\xa0\x12\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18', header,
                         'Incorrect mifareclassic_WriteDataBlock command')

    def test_mifareclassic_FormatNDEF(self):
        """mifareclassic_FormatNDEF correctly formats a card for NDEF"""
        frames = [
            (0, b'\x00'),
            (0, b'\x00'),
            (0, b'\x00'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status= nfc.mifareclassic_FormatNDEF()
        self.assertTrue(status, 'mifareclassic_FormatNDEF failed!')


        calls = [
            mock.call(b'\x40\x01\xa0\x01' + bytearray([0x14, 0x01, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1])),
            mock.call(b'\x40\x01\xa0\x02' + bytearray([0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1])),
            mock.call(b'\x40\x01\xa0\x03' + bytearray([0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0x78, 0x77, 0x88, 0xC1, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))  # key A
        ]
        interface.writeCommand.assert_has_calls(calls, any_order=True)

    def test_mifareclassic_WriteNDEFURI(self):
        """mifareclassic_WriteNDEFURI correctly formats a card for an  NDEF URI"""
        frames = [
            (0, b'\x00'),
            (0, b'\x00'),
            (0, b'\x00'),
            (0, b'\x00'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        tests = [
            (1, 'hi.org'),                  # len 6
            (2, 'foo.net'),                 # len 7
            (3, 'google.com'),              # len 10
            (4, 'looooooonnnnngggurl.zip'), # len 23
            (5, 'reallyloooooonnnnngggurl.zip'), # len 28
            (6, 'reeeaaaalllllllyloooooonnnnngggurl.zip'), # len 38
        ]

        with mock.patch.object(nfc, 'mifareclassic_WriteDataBlock') as mock_write_data_block:
            for url_id, url in tests:
                mock_write_data_block.reset_mock()
                status= nfc.mifareclassic_WriteNDEFURI(1, url_id, url)    # sector 0, 1=http://www.
                self.assertTrue(status, 'mifareclassic_FormatNDEF failed!')

                headers = [mock_write_data_block.call_args_list[i][0][1] for i in range(4)]
                ndef_data = b''.join(headers)
                self.assertLessEqual(len(ndef_data), 64, 'incorrect length of data')
                header = b'\x00\x00\x03' + bytearray([len(url) + 5]) + b'\xD1\x01' + bytearray([len(url) + 1, 0x55, url_id])
                ndef_pattern = (re.escape(header) + re.escape(bytes(url, 'utf-8')) + b'\xfe' + b'\x00*' +
                                 bytearray([0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7, 0x7F, 0x07, 0x88, 0x40, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))
                self.assertRegex(ndef_data, ndef_pattern, 'invalid sector format for url {}'.format(url))

    def test_mifareultralight_ReadPage(self):
        """mifareultralight_ReadPage correctly reads a page of data"""
        frames = [
            (0, b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status, data = nfc.mifareultralight_ReadPage(page=0x12)
        self.assertTrue(status, 'mifareultralight_ReadPage failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x40\x01\x30\x12', header, 'Incorrect mifareultralight_ReadPage command')
        self.assertEqual(b'\x01\x02\x03\x04', data, 'Incorrect data returned')  # Only first page is returned

    def test_mifareultralight_WritePage(self):
        """mifareultralight_WritePage correctly reads a data block"""
        frames = [
            (0, b'\x00'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status= nfc.mifareultralight_WritePage(page=0x12, buffer=b'\x01\x02\x03\x04\x05\x06')
        self.assertTrue(status, 'mifareultralight_WritePage failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x40\x01\xa2\x12\x01\x02\x03\x04', header, 'Incorrect mifareultralight_WritePage command')

    def test_felica_Polling(self):
        """felica_Polling correctly polls a FeliCa card"""
        frames = [
            (0, b'\x01\x05\x12\x01\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18'),
            (0, b'\x01\x05\x14\x01\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18\x0a\x0b'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status, idm, pwm, resp_code = nfc.felica_Polling(systemCode=0xfafb, requestCode=0x33)
        self.assertTrue(status, 'felica_Polling failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x4A\x01\x01\x00\xfa\xfb\x33\x00', header, 'Incorrect felica_Polling command')
        self.assertEqual(b'\x01\x02\x03\x04\x05\x06\x07\x08', idm, 'Incorrect idm returned')
        self.assertEqual(b'\x11\x12\x13\x14\x15\x16\x17\x18', pwm, 'Incorrect pwm returned')
        self.assertEqual(0, resp_code, 'Incorrect resp_code returned')

        status, idm, pwm, resp_code = nfc.felica_Polling(systemCode=0xfafb, requestCode=0x33)
        self.assertEqual(0x0a0b, resp_code, 'Incorrect resp_code returned')

    def test_felica_SendCommand(self):
        """felica_SendCommand correctly sends a FeliCa command"""
        frames = [
            (0, b'\x06\x04\xd1\xd2\xd3\xd4'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)
        nfc.inListedTag = 0x05

        status, response = nfc.felica_SendCommand(command=b'command')
        self.assertTrue(status, 'felica_SendCommand failed!')

        header = _get_header(interface)
        body = _get_body(interface)
        self.assertEqual(b'\x40\x05\x08', header, 'Incorrect felica_SendCommand command')
        self.assertEqual(b'command', body, 'Incorrect felica_SendCommand command')

    def test_felica_RequestService(self):
        """felica_RequestService correctly executes a FeliCa Request Service command"""
        frames = [
            (1, b'\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\x01\x00\x02\x00'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)
        nfc._felicaIDm = b'\x01\x02\x03\x04\x05\x06\x07\x08'

        with mock.patch.object(nfc, 'felica_SendCommand') as mock_send_cmd:
            mock_send_cmd.return_value = frames[0]
            status, key_versions = nfc.felica_RequestService(nodeCodeList=[0x0a01, 0x0a02])
            self.assertEqual(1, status, 'felica_RequestService failed!')

            command = mock_send_cmd.call_args[0][0]
            self.assertEqual(b'\x02\x01\x02\x03\x04\x05\x06\x07\x08\x02\x01\x0a\x02\x0a', command, 'Incorrect felica_RequestService command')
            self.assertEqual([1, 2], key_versions, 'Incorrect key versions returned')

    def test_felica_RequestResponse(self):
        """felica_RequestResponse correctly sends a FeliCa Request Response command"""
        frames = [
            (1, b'\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xd1'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)
        nfc._felicaIDm = b'\x01\x02\x03\x04\x05\x06\x07\x08'

        with mock.patch.object(nfc, 'felica_SendCommand') as mock_send_cmd:
            mock_send_cmd.return_value = frames[0]
            status, mode = nfc.felica_RequestResponse()
            self.assertEqual(1, status, 'felica_RequestResponse failed!')

            command = mock_send_cmd.call_args[0][0]
            self.assertEqual(b'\x04\x01\x02\x03\x04\x05\x06\x07\x08', command, 'Incorrect felica_RequestResponse command')
            self.assertEqual(0xD1, mode, 'Incorrect mode returned')

    def test_felica_ReadWithoutEncryption(self):
        """felica_ReadWithoutEncryption correctly sends a FeliCa Read Without Encryption command"""
        frames = [
            (1, b'\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\x00\x00\xfc' +
             b'\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18' +
             b'\x21\x22\x23\x24\x25\x26\x27\x28\x31\x32\x33\x34\x35\x36\x37\x38'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)
        nfc._felicaIDm = b'\x01\x02\x03\x04\x05\x06\x07\x08'

        with mock.patch.object(nfc, 'felica_SendCommand') as mock_send_cmd:
            mock_send_cmd.return_value = frames[0]
            status, block_data = nfc.felica_ReadWithoutEncryption(serviceCodeList=[0, 1], blockList=[3, 4])
            self.assertEqual(1, status, 'felica_ReadWithoutEncryption failed!')

            command = mock_send_cmd.call_args[0][0]
            self.assertEqual(b'\x06\x01\x02\x03\x04\x05\x06\x07\x08\x02\x00\x00\x01\x00\x02\x00\x03\x00\x04', command,
                             'Incorrect felica_ReadWithoutEncryption command')
            self.assertEqual([
                b'\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18',
                b'\x21\x22\x23\x24\x25\x26\x27\x28\x31\x32\x33\x34\x35\x36\x37\x38',
            ], block_data, 'Incorrect data returned')

    def test_felica_WriteWithoutEncryption(self):
        """felica_WriteWithoutEncryption correctly sends a FeliCa Write Without Encryption command"""
        frames = [
            (1, b'\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\x00\x00'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)
        nfc._felicaIDm = b'\x01\x02\x03\x04\x05\x06\x07\x08'

        with mock.patch.object(nfc, 'felica_SendCommand') as mock_send_cmd:
            mock_send_cmd.return_value = frames[0]
            block_data = [b'\x01\x02\x03\x04\x05\x06\x07\x08\x11\x12\x13\x14\x15\x16\x17\x18',
                          b'\x21\x22\x23\x24\x25\x26\x27\x28\x31\x32\x33\x34\x35\x36\x37\x38']
            status = nfc.felica_WriteWithoutEncryption(serviceCodeList=[0, 1], blockList=[3, 4], blockData=block_data)
            self.assertEqual(1, status, 'felica_WriteWithoutEncryption failed!')

            command = mock_send_cmd.call_args[0][0]
            self.assertEqual((b'\x08\x01\x02\x03\x04\x05\x06\x07\x08\x02\x00\x00\x01\x00\x02\x00\x03\x00\x04'
                              + block_data[0] + block_data[1]), command,
                             'Incorrect felica_WriteWithoutEncryption command')

    def test_felica_RequestSystemCode(self):
        """felica_RequestSystemCode correctly sends a FeliCa Request System code command"""
        frames = [
            (1, b'\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\x02\x00\xd1\x00\xd2'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)
        nfc._felicaIDm = b'\x01\x02\x03\x04\x05\x06\x07\x08'

        with mock.patch.object(nfc, 'felica_SendCommand') as mock_send_cmd:
            mock_send_cmd.return_value = frames[0]
            status, sys_codes = nfc.felica_RequestSystemCode()
            self.assertEqual(1, status, 'felica_RequestSystemCode failed!')

            command = mock_send_cmd.call_args[0][0]
            self.assertEqual(b'\x0C\x01\x02\x03\x04\x05\x06\x07\x08', command,
                             'Incorrect felica_RequestSystemCode command')
            self.assertEqual([0xd1, 0xd2], sys_codes, 'Incorrect system codes returned')

    def test_felica_Release(self):
        """felica_Release correctly sends a FeliCa Release command"""
        frames = [
            (0, b'\x00'),
        ]
        interface = _mock_interface(resp_frames=frames)
        nfc = Pn532(interface)

        status = nfc.felica_Release()
        self.assertEqual(1, status, 'felica_Release failed!')

        header = _get_header(interface)
        self.assertEqual(b'\x52\x00', header, 'Incorrect felica_Release command')
