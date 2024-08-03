"""
    @file     PN532.cpp
    @author   Adafruit Industries & Seeed Studio
    @license  BSD

"""
from typing import List, NamedTuple

from pn532pi.interfaces.pn532Interface import Pn532Interface, PN532_TIMEOUT

# PN532 Commands
from pn532pi.nfc.pn532_log import DMSG, DMSG_HEX

PN532_COMMAND_DIAGNOSE              = (0x00)
PN532_COMMAND_GETFIRMWAREVERSION    = (0x02)
PN532_COMMAND_GETGENERALSTATUS      = (0x04)
PN532_COMMAND_READREGISTER          = (0x06)
PN532_COMMAND_WRITEREGISTER         = (0x08)
PN532_COMMAND_READGPIO              = (0x0C)
PN532_COMMAND_WRITEGPIO             = (0x0E)
PN532_COMMAND_SETSERIALBAUDRATE     = (0x10)
PN532_COMMAND_SETPARAMETERS         = (0x12)
PN532_COMMAND_SAMCONFIGURATION      = (0x14)
PN532_COMMAND_POWERDOWN             = (0x16)
PN532_COMMAND_RFCONFIGURATION       = (0x32)
PN532_COMMAND_RFREGULATIONTEST      = (0x58)
PN532_COMMAND_INJUMPFORDEP          = (0x56)
PN532_COMMAND_INJUMPFORPSL          = (0x46)
PN532_COMMAND_INLISTPASSIVETARGET   = (0x4A)
PN532_COMMAND_INATR                 = (0x50)
PN532_COMMAND_INPSL                 = (0x4E)
PN532_COMMAND_INDATAEXCHANGE        = (0x40)
PN532_COMMAND_INCOMMUNICATETHRU     = (0x42)
PN532_COMMAND_INDESELECT            = (0x44)
PN532_COMMAND_INRELEASE             = (0x52)
PN532_COMMAND_INSELECT              = (0x54)
PN532_COMMAND_INAUTOPOLL            = (0x60)
PN532_COMMAND_TGINITASTARGET        = (0x8C)
PN532_COMMAND_TGSETGENERALBYTES     = (0x92)
PN532_COMMAND_TGGETDATA             = (0x86)
PN532_COMMAND_TGSETDATA             = (0x8E)
PN532_COMMAND_TGSETMETADATA         = (0x94)
PN532_COMMAND_TGGETINITIATORCOMMAND = (0x88)
PN532_COMMAND_TGRESPONSETOINITIATOR = (0x90)
PN532_COMMAND_TGGETTARGETSTATUS     = (0x8A)

PN532_RESPONSE_INDATAEXCHANGE       = (0x41)
PN532_RESPONSE_INLISTPASSIVETARGET  = (0x4B)

# Baud Rate selectors
PN532_MIFARE_ISO14443A_106KBPS      = (0x00)
PN532_FELICA_212KBPS                = (0x01)
PN532_FELICA_424KBPS                = (0x02)
PN532_MIFARE_ISO14443B_106KBPS      = (0x03)
PN532_JEWEL_106KBPS                 = (0x04)

# Mifare Commands
MIFARE_CMD_AUTH_A                   = (0x60)
MIFARE_CMD_AUTH_B                   = (0x61)
MIFARE_CMD_READ                     = (0x30)
MIFARE_CMD_WRITE                    = (0xA0)
MIFARE_CMD_WRITE_ULTRALIGHT         = (0xA2)
MIFARE_CMD_TRANSFER                 = (0xB0)
MIFARE_CMD_DECREMENT                = (0xC0)
MIFARE_CMD_INCREMENT                = (0xC1)
MIFARE_CMD_STORE                    = (0xC2)

# FeliCa Commands
FELICA_CMD_POLLING                  = (0x00)
FELICA_CMD_REQUEST_SERVICE          = (0x02)
FELICA_CMD_REQUEST_RESPONSE         = (0x04)
FELICA_CMD_READ_WITHOUT_ENCRYPTION  = (0x06)
FELICA_CMD_WRITE_WITHOUT_ENCRYPTION = (0x08)
FELICA_CMD_REQUEST_SYSTEM_CODE      = (0x0C)

# Prefixes for NDEF Records (to identify record type)
NDEF_URIPREFIX_NONE                 = (0x00)
NDEF_URIPREFIX_HTTP_WWWDOT          = (0x01)
NDEF_URIPREFIX_HTTPS_WWWDOT         = (0x02)
NDEF_URIPREFIX_HTTP                 = (0x03)
NDEF_URIPREFIX_HTTPS                = (0x04)
NDEF_URIPREFIX_TEL                  = (0x05)
NDEF_URIPREFIX_MAILTO               = (0x06)
NDEF_URIPREFIX_FTP_ANONAT           = (0x07)
NDEF_URIPREFIX_FTP_FTPDOT           = (0x08)
NDEF_URIPREFIX_FTPS                 = (0x09)
NDEF_URIPREFIX_SFTP                 = (0x0A)
NDEF_URIPREFIX_SMB                  = (0x0B)
NDEF_URIPREFIX_NFS                  = (0x0C)
NDEF_URIPREFIX_FTP                  = (0x0D)
NDEF_URIPREFIX_DAV                  = (0x0E)
NDEF_URIPREFIX_NEWS                 = (0x0F)
NDEF_URIPREFIX_TELNET               = (0x10)
NDEF_URIPREFIX_IMAP                 = (0x11)
NDEF_URIPREFIX_RTSP                 = (0x12)
NDEF_URIPREFIX_URN                  = (0x13)
NDEF_URIPREFIX_POP                  = (0x14)
NDEF_URIPREFIX_SIP                  = (0x15)
NDEF_URIPREFIX_SIPS                 = (0x16)
NDEF_URIPREFIX_TFTP                 = (0x17)
NDEF_URIPREFIX_BTSPP                = (0x18)
NDEF_URIPREFIX_BTL2CAP              = (0x19)
NDEF_URIPREFIX_BTGOEP               = (0x1A)
NDEF_URIPREFIX_TCPOBEX              = (0x1B)
NDEF_URIPREFIX_IRDAOBEX             = (0x1C)
NDEF_URIPREFIX_FILE                 = (0x1D)
NDEF_URIPREFIX_URN_EPC_ID           = (0x1E)
NDEF_URIPREFIX_URN_EPC_TAG          = (0x1F)
NDEF_URIPREFIX_URN_EPC_PAT          = (0x20)
NDEF_URIPREFIX_URN_EPC_RAW          = (0x21)
NDEF_URIPREFIX_URN_EPC              = (0x22)
NDEF_URIPREFIX_URN_NFC              = (0x23)

PN532_GPIO_VALIDATIONBIT            = (0x80)
PN532_GPIO_P30                      = (0)
PN532_GPIO_P31                      = (1)
PN532_GPIO_P32                      = (2)
PN532_GPIO_P33                      = (3)
PN532_GPIO_P34                      = (4)
PN532_GPIO_P35                      = (5)

# FeliCa consts
FELICA_READ_MAX_SERVICE_NUM         = 16
FELICA_READ_MAX_BLOCK_NUM           = 12 # for typical FeliCa card
FELICA_WRITE_MAX_SERVICE_NUM        = 16
FELICA_WRITE_MAX_BLOCK_NUM          = 10 # for typical FeliCa card
FELICA_REQ_SERVICE_MAX_NODE_NUM     = 32

# Support options in FW Version Info
SUPPORTS_ISO18092 = 0b100
SUPPORTS_ISO14443_A = 0b010
SUPPORTS_ISO14443_B = 0b001
class Pn532FirmwareInfo(NamedTuple):
    """
    Information contained in the response to the 
    GetFirmwareVersion command
    """
    ic_version: int
    fw_major: int
    fw_minor: int
    support_opts: int
    iso18092: bool
    iso14443_a: bool
    iso14443_b: bool

    def __str__(self) -> str:
        all_opts = [('ISO18092', self.iso18092), ('ISO4443-A', self.iso14443_a), 
                    ('ISO4443-B', self.iso14443_b)]
        opts = [name for name, supported in all_opts if supported]
        return (f'Pn532FirmwareInfo(IC Version: {hex(self.ic_version)}, '
                f'FW Version: {self.fw_major}.{self.fw_minor}, '
                f'Supports: {opts} ({hex(self.support_opts)}))')
    
    def __repr__(self) -> str:
        return str(self)

class Pn532:
    def __init__(self, interface: Pn532Interface):
        self._interface = interface

        self._uid = []  # ISO14443A uid
        self._uidLen = 0  # uid len
        self._key = []  # Mifare Classic key
        self.inListedTag = 0 # Tg number of inlisted tag.
        self._felicaIDm = bytearray() # FeliCa IDm (NFCID2)
        self._felicaPMm = bytearray() # FeliCa PMm (PAD)

    def begin(self):
        """
        Setups the HW
        """
        self._interface.begin()
        self._interface.wakeup()

    def getFirmwareVersion(self) -> int:
        """
        Checks the firmware version of the PN5xx chip

        See https://www.nxp.com/docs/en/user-guide/141520.pdf page 73

        :returns:  The chip's firmware version and ID
        """
        if (self._interface.writeCommand(bytearray([PN532_COMMAND_GETFIRMWAREVERSION]))):
            return 0

        # read data packet
        status, response = self._interface.readResponse()
        if (status < 0):
            return 0

        # response = self.pn532_packetbuffer[0]
        # response <<= 8
        # response |= self.pn532_packetbuffer[1]
        # response <<= 8
        # response |= self.pn532_packetbuffer[2]
        # response <<= 8
        # response |= self.pn532_packetbuffer[3]

        return int.from_bytes(response, byteorder='big')
    
    def getFirmwareInfo(self) -> tuple:
        """
        Parse the firmware version info into its separate parts
        Format: |ic_version[8] | fw_version[8] | fw_revision[8] | support_opts[8]|
        """
        firmware_data = self.getFirmwareVersion()
        opts, fw_min, fw_maj, ic_ver = [(firmware_data >> i) & 0xFF for i in range(0, 32, 8)]

        return Pn532FirmwareInfo(ic_ver, fw_maj, fw_min, opts, 
                                 bool(opts & SUPPORTS_ISO18092), 
                                 bool(opts & SUPPORTS_ISO14443_A),
                                 bool(opts & SUPPORTS_ISO14443_B))


    def readRegister(self, reg: int) -> int:
        """
        Read a PN532 register.

        :param reg:  the 16-bit register address.

        :returns:  The register value.
        """
        header = bytearray([PN532_COMMAND_READREGISTER, ((reg >> 8) & 0xFF), reg & 0xFF])

        if (self._interface.writeCommand(header)):
            return 0

        # read data packet
        status, response = self._interface.readResponse()
        if (0 > status):
            return 0

        return response[0]

    def writeRegister(self, reg: int, val: int) -> int:
        """
        Write to a PN532 register.

        :param  reg:  the 16-bit register address.
        :param  val:  the 8-bit value to write.

        :returns:  0 for failure, 1 for success.
        """
        header = bytearray([PN532_COMMAND_WRITEREGISTER, ((reg >> 8) & 0xFF), (reg & 0xFF), (val & 0xFf)])

        if (self._interface.writeCommand(header)):
            return 0
        

        # read data packet
        status, response = self._interface.readResponse()
        if (0 > status):
            return 0

        return 1

    def writeGPIO(self,  pinstate: int) -> bool:
        """
        Writes an 8-bit value that sets the state of the PN532's GPIO  (P3)

        :warning: This function is provided exclusively for board testing and
                 is dangerous since it will throw an error if any pin other
                 than the ones marked "Can be used as GPIO" are modified!  All
                 pins that can not be used as GPIO should ALWAYS be left high
                 (value = 1) or the system will become unstable and a HW reset
                 will be required to recover the PN532.

                 pinState[0]  = P30     Can be used as GPIO
                 pinState[1]  = P31     Can be used as GPIO
                 pinState[2]  = P32     *** RESERVED (Must be 1!) ***
                 pinState[3]  = P33     Can be used as GPIO
                 pinState[4]  = P34     *** RESERVED (Must be 1!) ***
                 pinState[5]  = P35     Can be used as GPIO

        :returns 1 if everything executed properly, 0 for an error
        """
    
        # Make sure pinstate does not try to toggle P32 or P34
        pinstate |= (1 << PN532_GPIO_P32) | (1 << PN532_GPIO_P34)

        # Fill command buffer
        header = bytearray([PN532_COMMAND_WRITEGPIO,
                            (PN532_GPIO_VALIDATIONBIT | pinstate),  # P3 Pins
                            0x00])  # P7 GPIO Pins (not used ... taken by I2C)

        DMSG("Writing P3 GPIO: ")
        DMSG_HEX(header)
        DMSG("\n")

        # Send the WRITEGPIO command (0x0E)
        if (self._interface.writeCommand(header)):
            return False

        status, response = self._interface.readResponse()
        return status >= 0

    def readGPIO(self) -> int:
        """
            Reads the state of the PN532's GPIO pins (P3)

            :returns: An 8-bit value containing the pin state where:

                 pinState[0]  = P30
                 pinState[1]  = P31
                 pinState[2]  = P32
                 pinState[3]  = P33
                 pinState[4]  = P34
                 pinState[5]  = P35 
        """
    
        header = bytearray([PN532_COMMAND_READGPIO])

        # Send the READGPIO command (0x0C)
        if (self._interface.writeCommand(header)):
            return 0x0

        status, response = self._interface.readResponse()
        # READGPIO response without prefix and suffix should be in the following format:
        # 
        #   byte            Description
        #   -------------   ------------------------------------------
        #   b0              P3 GPIO Pins
        #   b1              P7 GPIO Pins (not used ... taken by I2C)
        #   b2              Interface Mode Pins (not used ... bus select pins)

        DMSG("P3 GPIO: ") 
        DMSG_HEX(response[0])
        DMSG("P7 GPIO: ") 
        DMSG_HEX(response[1])
        DMSG("I0I1 GPIO: ") 
        DMSG_HEX(response[2])
        DMSG("\n")

        return response[0]
    
    def SAMConfig(self) -> bool:
        """
        Configures the SAM (Secure Access Module)
        :returns: True if success, False if error
        """
        header = bytearray([PN532_COMMAND_SAMCONFIGURATION,
                            0x01,   # normal mode
                            0x14,   # timeout 50ms * 20 = 1 second
                            0x01])  # use IRQ pin!

        DMSG("SAMConfig\n")

        if (self._interface.writeCommand(header)):
            return False

        status, response = self._interface.readResponse()
        return status >= 0
    

    def setPassiveActivationRetries(self, maxRetries: int) -> bool:
        """
        Sets the MxRtyPassiveActivation uint8_t of the RFConfiguration register

        :param  maxRetries:    0xFF to wait forever, 0x00..0xFE to timeout
                              after mxRetries

        :returns: True if everything executed properly, False for an error
        """
        header = bytearray([PN532_COMMAND_RFCONFIGURATION,
                            5,  # Config item 5 (MaxRetries)
                            0xFF,  # MxRtyATR (default = 0xFF)
                            0x01,  # MxRtyPSL (default = 0x01)
                            maxRetries & 0xFF,
                            ])

        if (self._interface.writeCommand(header)):
            return False  # no ACK

        status, response = self._interface.readResponse()
        return (status >=  0)

    def setRFField(self, autoRFCA: bool, RFOn: bool) -> bool:
        """
        Sets the RFon/off uint8_t of the RFConfiguration register

        :param  autoRFCA:    False: No check of the external field before
                            activation

                            True: Check the external field before
                            activation

        :param  RFOn:    False Switch the RF field off, True: switch the RF
                        field on

        :returns:    True if everything executed properly, False for an error
        """
        header = bytearray([
            PN532_COMMAND_RFCONFIGURATION,
            1,
            (0x2 if autoRFCA else 0) | (0x1 if RFOn else 0)
        ])
        if(self._interface.writeCommand(header)):
            return False  # no ACK

        status, response = self._interface.readResponse()
        return (status >= 0)
    
    # **** ISO14443A Commands *****

    def readPassiveTargetID(self, cardbaudrate: int, timeout: int = 1000, inlist: bool = False) -> (bool, bytearray):
        """
        Waits for an ISO14443A target to enter the field

        :param  cardBaudRate:  Baud rate of the card
        :param  timeout:       The number of tries before timing out
        :param  inlist:        If set to True, the card will be inlisted

        :returns: (True if successful, uid of the card)
        """
        header = bytearray([
            PN532_COMMAND_INLISTPASSIVETARGET,
            1,  # max 1 cards at once (we can set this to 2 later)
            cardbaudrate & 0xFF,
        ])
        if (self._interface.writeCommand(header)) :
            return False, bytearray()  # command failed


        # read data packet
        status, response = self._interface.readResponse(timeout)
        if (status < 0):
            return False, bytearray()
        
        # check some basic stuff
        # ISO14443A card response should be in the following format:

          # byte            Description
          # -------------   ------------------------------------------
          # b0              Tags Found
          # b1              Tag Number (only one used in this example)
          # b2..3           SENS_RES
          # b4              SEL_RES
          # b5              NFCID Length
          # b6..NFCIDLen    NFCID

        if (response[0] != 1):
            return False, bytearray()

        sens_res = response[2]
        sens_res <<= 8
        sens_res |= response[3]

        DMSG("ATQA: 0x")
        DMSG_HEX(sens_res)
        DMSG("SAK: 0x")
        DMSG_HEX(response[4])
        DMSG("\n")

        # Card appears to be Mifare Classic 
        uidLength = response[5]
        uid = bytearray(response[6:6 + uidLength])

        if (inlist) :
            self.inListedTag = response[1]
        
        return True, uid
    
    # **** Mifare Classic Functions *****

    def mifareclassic_IsFirstBlock (self, uiBlock: int) -> bool:
        """
          Indicates whether the specified block number is the first block
          in the sector (block 0 relative to the current sector) 
        """
    
        # Test if we are in the small or big sectors
        if (uiBlock < 128):
            return ((uiBlock) % 4 == 0)
        else:
            return ((uiBlock) % 16 == 0)

    def mifareclassic_IsTrailerBlock(self, uiBlock: int) -> bool:
        """
        Indicates whether the specified block number is the sector trailer
        """
    
        # Test if we are in the small or big sectors
        if (uiBlock < 128):
            return ((uiBlock + 1) % 4 == 0)
        else:
            return ((uiBlock + 1) % 16 == 0)

    def mifareclassic_AuthenticateBlock(self, uid: bytearray, blockNumber: int, keyNumber: int, keyData: bytearray) -> bool:
        """
                Tries to authenticate a block of memory on a MIFARE card using the
        INDATAEXCHANGE command.  See section 7.3.8 of the PN532 User Manual
        for more information on sending MIFARE and other commands.

        :param  uid:           Pointer to a byte array containing the card UID
        :param  blockNumber:   The block number to authenticate.  (0..63 for
                              1KB cards, and 0..255 for 4KB cards).
        :param  keyNumber:     Which key type to use during authentication
                              (0 = MIFARE_CMD_AUTH_A, 1 = MIFARE_CMD_AUTH_B)
        :param  keyData:       Pointer to a byte array containing the 6 bytes
                              key value

        :returns: True if everything executed properly, False for an error
        """
    
        # Hang on to the key and uid data
        self._key = keyData
        self._uid = uid

        # Prepare the authentication command #
        header = bytearray([PN532_COMMAND_INDATAEXCHANGE,
                  1,
                  MIFARE_CMD_AUTH_B if keyNumber else MIFARE_CMD_AUTH_A,
                  blockNumber])
        header += self._key[:6] + self._uid

        if (self._interface.writeCommand(header)):
            return False

        # Read the response packet
        status, response = self._interface.readResponse()

        # Check if the response is valid and we are authenticated???
        # for an auth success it should be bytes 5-7: 0xD5 0x41 0x00
        # Mifare auth error is technically byte 7: 0x14 but anything other and 0x00 is not good
        if (status < 0 or response[0] != 0x00):
            DMSG("Authentication failed\n")
            return False

        return True

    def mifareclassic_ReadDataBlock (self, blockNumber: int) -> (bool, bytearray):
        """
        Tries to read an entire 16-bytes data block at the specified block
        address.

        :param  blockNumber:   The block number to authenticate.  (0..63 for
                              1KB cards, and 0..255 for 4KB cards).
        :param  data:          Pointer to the byte array that will hold the
                              retrieved data (if any)

        :returns: tuple (result, data)
            result: bool True if operation was successful, False if error
            data: bytearray data read
        """
    
        DMSG("Trying to read 16 bytes from block ")
        DMSG(blockNumber)

        #  Prepare the command
        header = bytearray([
            PN532_COMMAND_INDATAEXCHANGE,
            1,                  # Card number
            MIFARE_CMD_READ,    # Mifare Read command = 0x30
            blockNumber,        # Block Number (0..63 for 1K, 0..255 for 4K)
        ])
        #  Send the command 
        if (self._interface.writeCommand(header)):
            return False, bytearray()
        

        #  Read the response packet 
        status, response = self._interface.readResponse()

        #  If byte 8 isn't 0x00 we probably have an error 
        if (status < 0 or response[0] != 0x00):
            DMSG("Authentication failed\n")
            return False, bytearray()

        #  Copy the 16 data bytes to the output buffer        
        #  Block content starts at byte 9 of a valid response
        return True, response[1:17]
    
    def mifareclassic_WriteDataBlock (self, blockNumber: int, data: bytearray) -> bool:
        """
                Tries to write an entire 16-bytes data block at the specified block
        address.

        :param  blockNumber:   The block number to authenticate.  (0..63 for
                              1KB cards, and 0..255 for 4KB cards).
        :param  data:          The byte array that contains the data to write.

        :returns: True if everything executed properly, False for an error
        """

        #  Prepare the first command
        header = bytearray([PN532_COMMAND_INDATAEXCHANGE, 1, MIFARE_CMD_WRITE, blockNumber]) + data[:16]

        #  Send the command 
        if (self._interface.writeCommand(header)):
            return False
        
        #  Read the response packet
        status, response = self._interface.readResponse()

        return (status >= 0)

    def mifareclassic_FormatNDEF (self) -> bool:
        """
                Formats a Mifare Classic card to store NDEF Records

        :returns: True if everything executed properly, False for an error
        """
    
        sectorbuffer1 = bytearray([0x14, 0x01, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1])
        sectorbuffer2 = bytearray([0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1])
        sectorbuffer3 = bytearray([0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0x78, 0x77, 0x88, 0xC1, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

        # Note 0xA0 0xA1 0xA2 0xA3 0xA4 0xA5 must be used for key A
        # for the MAD sector in NDEF records (sector 0)

        # Write block 1 and 2 to the card
        if (not (self.mifareclassic_WriteDataBlock(1, sectorbuffer1))):
            return False
        if (not (self.mifareclassic_WriteDataBlock(2, sectorbuffer2))):
            return False
        # Write key A and access rights card
        if (not (self.mifareclassic_WriteDataBlock(3, sectorbuffer3))):
            return False

        # Seems that everything was OK (?!)
        return True

    def mifareclassic_WriteNDEFURI (self, sectorNumber: int, uriIdentifier: int, url: str) -> bool:
        """
        Writes an NDEF URI Record to the specified sector (1..15)

        Note that this function assumes that the Mifare Classic card is
        already formatted to work as an "NFC Forum Tag" and uses a MAD1
        file system.  You can use the NXP TagWriter app on Android to
        properly format cards for this.

        :param  sectorNumber:  The sector that the URI record should be written
                              to (can be 1..15 for a 1K card)
        :param  uriIdentifier: The uri identifier code (0 = none, 0x01 =
                              "http://www.", etc.)
        :param  url:           The uri text to write (max 38 characters).

        :return: True if everything executed properly, False for an error
        """

        # Figure out how long the string is
        url_bytes = bytearray(url, 'ascii')
        length = len(url_bytes)

        # Make sure we're within a 1K limit for the sector number
        if ((sectorNumber < 1) or (sectorNumber > 15)):
            return False

        # Make sure the URI payload is between 1 and 38 chars
        if ((length < 1) or (length > 38)):
            return False

        # Note 0xD3 0xF7 0xD3 0xF7 0xD3 0xF7 must be used for key A
        # in NDEF records

        # Setup the sector buffer (w/pre-formatted TLV wrapper and NDEF message)
        sectorbuffer1 = bytearray([0x00, 0x00, 0x03, length + 5, 0xD1, 0x01, length + 1, 0x55, uriIdentifier, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        sectorbuffer2 = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        sectorbuffer3 = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        sectorbuffer4 = bytearray([0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7, 0x7F, 0x07, 0x88, 0x40, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # TODO: This can probably be simplified...
        if (length <= 6) :
            # Unlikely we'll get a url this short, but why not ...
            sectorbuffer1 = sectorbuffer1[:9] + url_bytes[:length] + sectorbuffer1[9 + length:]
            sectorbuffer1[length + 9] = 0xFE
        elif (length == 7):
            # 0xFE needs to be wrapped around to next block
            sectorbuffer1 = sectorbuffer1[:9] + url_bytes[:length] + sectorbuffer1[9 + length:]
            sectorbuffer2[0] = 0xFE
        elif ((length > 7) and (length <= 22)):
            # Url fits in two blocks
            sectorbuffer1 = sectorbuffer1[:9] + url_bytes[:7] + sectorbuffer1[9 + 7:]
            sectorbuffer2 = url_bytes[7:] + sectorbuffer2[length - 7:]
            sectorbuffer2[length - 7] = 0xFE
        elif (length == 23):
            # 0xFE needs to be wrapped around to final block
            sectorbuffer1 = sectorbuffer1[:9] + url_bytes[:7] + sectorbuffer1[9 + 7:]
            sectorbuffer2 = url_bytes[7:]
            sectorbuffer3[0] = 0xFE
        else:
            # Url fits in three blocks
            sectorbuffer1 = sectorbuffer1[:9] + url_bytes[:7] + sectorbuffer1[9 + 7:]
            sectorbuffer2 = url_bytes[7:23]
            sectorbuffer3 = url_bytes[23:] + sectorbuffer3[length - 23:]
            sectorbuffer3[length - 23] = 0xFE

        # Now write all three blocks back to the card
        if (not (self.mifareclassic_WriteDataBlock(sectorNumber * 4, sectorbuffer1))):
            return False
        if (not (self.mifareclassic_WriteDataBlock((sectorNumber * 4) + 1, sectorbuffer2))):
            return False
        if (not (self.mifareclassic_WriteDataBlock((sectorNumber * 4) + 2, sectorbuffer3))):
            return False
        if (not (self.mifareclassic_WriteDataBlock((sectorNumber * 4) + 3, sectorbuffer4))):
            return False

        # Seems that everything was OK (?!)
        return True

    # **** Mifare Ultralight Functions *****

    def mifareultralight_ReadPage(self, page: int) -> (bool, bytearray):
        """
                Tries to read an entire 4-bytes page at the specified address.

        :param  page:        The page number (0..63 in most cases)
        :returns: (result, data)
                result: bool True if successful, False if error
                data: bytearray received page data
        """

        #  Prepare the command
        header = bytearray([
            PN532_COMMAND_INDATAEXCHANGE,
            1,                   #  Card number
            MIFARE_CMD_READ,     #  Mifare Read command = 0x30
            page,                #  Page Number (0..63 in most cases)
        ])
        #  Send the command 
        if (self._interface.writeCommand(header)):
            return False, bytearray()
        

        #  Read the response packet 
        status, response = self._interface.readResponse()

        #  If byte 8 isn't 0x00 we probably have an error
        if (status < 0 or response[0] != 0x00):
            DMSG("Authentication failed\n")
            return False, bytearray()

        #  Copy the 4 data bytes to the output buffer
        #  Block content starts at byte 9 of a valid response
        #  Note that the command actually reads 16 bytes or 4
        #  pages at a time ... we simply discard the last 12
        #  bytes
        data = response[1:5]
        return True, data

    def mifareultralight_WritePage(self, page: int, buffer: bytearray) -> bool:
        """
        Tries to write an entire 4-bytes data buffer at the specified page
        address.

        :param  page:     The page number to write into.  (0..63).
        :param  buffer:   The byte array that contains the data to write.

        :returns: True if everything executed properly, False for an error
        """
    
        #  Prepare the first command 
        header = bytearray([PN532_COMMAND_INDATAEXCHANGE, 1, MIFARE_CMD_WRITE_ULTRALIGHT, page])
        header += buffer[:4]

        #  Send the command 
        if (self._interface.writeCommand(header)):
            return False

        #  Read the response packet
        status, response = self._interface.readResponse()
        return status >= 0

    def inDataExchange(self, send: bytearray) -> (bool, bytearray):
        """
                Exchanges an APDU with the currently inlisted peer

        :param  send:            Pointer to data to send
        :param  response:        Pointer to response data
        :param  responseLength:  Pointer to the response data length
        """

        header = bytearray([
            0x40,  # PN532_COMMAND_INDATAEXCHANGE
            self.inListedTag
        ])

        if (self._interface.writeCommand(header, send)):
            return False, bytearray()
        

        status, response = self._interface.readResponse()
        if (status < 0):
            return False, bytearray()
        

        if ((response[0] & 0x3f) != 0):
            DMSG("Status code indicates an error\n")
            return False, bytearray()

        response = response[1:]
        return True, response

    def inListPassiveTarget(self) -> bool:
        """
            'InLists' a passive target. PN532 acting as reader/initiator,
            peer acting as card/responder.
            :returns: True if command succeeded, False otherwise
        """
        header = bytearray([
            PN532_COMMAND_INLISTPASSIVETARGET,
            1,
            0,
        ])
        DMSG("inList passive target\n")

        if (self._interface.writeCommand(header)):
            return False

        status, response = self._interface.readResponse()
        if (status < 0 or response[0] != 1):
            return False
        
        self.inListedTag = response[1]

        return True

    def tgInitAsTarget(self, command: bytearray, timeout: int) -> int:

        status = self._interface.writeCommand(command)
        if (status < 0):
            return -1

        status, response = self._interface.readResponse(timeout)
        if (status > 0):
            return 1
        elif(PN532_TIMEOUT == status):
            return 0
        else:
            return -2

    def tgInitAsTargetP2P(self, timeout: int) -> int:
        """
         * Peer to Peer

         """

        command = bytearray([
            PN532_COMMAND_TGINITASTARGET,
            0,
            0x00, 0x00,  # SENS_RES
            0x00, 0x00, 0x00,  # NFCID1
            0x40,  # SEL_RES

            0x01, 0xFE, 0x0F, 0xBB, 0xBA, 0xA6, 0xC9, 0x89,  # POL_RES
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0xFF, 0xFF,

            0x01, 0xFE, 0x0F, 0xBB, 0xBA, 0xA6, 0xC9, 0x89, 0x00, 0x00,  # NFCID3t: Change this to desired value

            0x0a, 0x46, 0x66, 0x6D, 0x01, 0x01, 0x10, 0x02, 0x02, 0x00, 0x80,
            # LLCP magic number, version parameter and MIUX
            0x00])

        return self.tgInitAsTarget(command, timeout)

    def tgGetData(self) -> (int, bytearray):
    
        header = bytearray([PN532_COMMAND_TGGETDATA])

        if (self._interface.writeCommand(header)):
            return -1, bytearray()
        

        status, response = self._interface.readResponse()
        if (0 >= status):
            return status, bytearray()

        length = status - 1

        if (response[0] != 0):
            DMSG("status is not ok\n")
            return -5, bytearray()

        response = response[1:]
        return length, response
    

    def tgSetData(self, header: bytearray, body: bytearray = bytearray()) -> bool:
        header = bytearray([PN532_COMMAND_TGSETDATA]) + header

        if (self._interface.writeCommand(header, body)):
            return False

        status, response = self._interface.readResponse()
        if (0 > status):
            return False

        if (0 != response[0]):
            return False

        return True

    def inRelease(self, relevantTarget: int = 0) -> bool:
        header = bytearray([
            PN532_COMMAND_INRELEASE,
            relevantTarget,
        ])
        if (self._interface.writeCommand(header)):
            return False

        # read data packet
        status, response = self._interface.readResponse()
        return status >= 0

    def felica_Polling(self, systemCode: int, requestCode: int, timeout: int = 1000) -> (int, bytearray, bytearray, int):
        """
            Poll FeliCa card. PN532 acting as reader/initiator,
            peer acting as card/responder.
            :param timeout:
            :param  systemCode:             Designation of System Code. When sending FFFFh as System Code,
                                               all FeliCa cards can return response.
            :param  requestCode:            Designation of Request Data as follows:
                                                 00h: No Request
                                                 01h: System Code request (to acquire System Code of the card)
                                                 02h: Communication performance request
            :returns: (status, idm, pwm, systemCodeResponse)
                        status                 0 = no card, 1 = FeliCa card detected, <0 = error
                        idm                    IDm of the card (8 bytes)
                        pmm                    PMm of the card (8 bytes)
                        systemCodeResponse     System Code of the card (Optional, 2bytes)
        """
        header = bytearray([
        PN532_COMMAND_INLISTPASSIVETARGET,
        1,
        1,
        FELICA_CMD_POLLING,
        (systemCode >> 8) & 0xFF,
        systemCode & 0xFF,
        requestCode & 0xFF,
        0,
        ])
        no_data = bytearray()

        if (self._interface.writeCommand(header)):
            DMSG("Could not send Polling command\n")
            return -1, no_data, no_data, 0

        status, response = self._interface.readResponse(timeout)
        if (status < 0):
            DMSG("Could not receive response\n")
            return -2, no_data, no_data, 0

        # Check NbTg (response[7])
        if (response[0] == 0):
            DMSG("No card had detected\n")
            return 0, no_data, no_data, 0
        elif (response[0] != 1):
            DMSG("Unhandled number of targets inlisted. NbTg: ")
            DMSG_HEX(response[7])
            DMSG("\n")
            return -3, no_data, no_data, 0

        self.inListedTag = response[1]
        DMSG("Tag number: ")
        DMSG_HEX(response[1])
        DMSG("\n")

        # length check
        responseLength = response[2]
        if (responseLength != 18 and responseLength != 20):
            DMSG("Wrong response length\n")
            return -4, no_data, no_data, 0

        idm = response[4:12]
        pwm = response[12:24]
        self._felicaIDm = idm
        self._felicaPMm = pwm

        if (responseLength == 20):
            systemCodeResponse = (response[20] << 8) + response[21]
        else:
            systemCodeResponse = 0

        return 1, idm, pwm, systemCodeResponse

    def felica_SendCommand(self, command: bytearray) -> (int, bytearray):
        """
            Sends FeliCa command to the currently inlisted peer

            :param  command:         FeliCa command packet. (e.g. 00 FF FF 00 00  for Polling command)
            :returns:  (status, response)
                        status 1: Success, < 0: error
                        response: FeliCa response packet. (e.g. 01 NFCID2(8 bytes) PAD(8 bytes)  for Polling response)
        """
        commandlength = len(command)
        no_data = bytearray()

        if (commandlength > 0xFE):
            DMSG("Command length too long\n")
            return -1, no_data

        header = bytearray([
            PN532_COMMAND_INDATAEXCHANGE,
            self.inListedTag,
            commandlength + 1,
        ])
        if (self._interface.writeCommand(header, command)):
            DMSG("Could not send FeliCa command\n")
            return -2, no_data

        # Wait card response
        status, response = self._interface.readResponse()
        if (status < 0):
            DMSG("Could not receive response\n")
            return -3, no_data

        # Check status (response[0])
        if ((response[0] & 0x3F) != 0):
            DMSG("Status code indicates an error: ")
            DMSG_HEX(response[0])
            DMSG("\n")
            return -4, no_data

        # length check
        responseLength = response[1] - 1
        if ((status - 2) !=  responseLength):
            DMSG("Wrong response length\n")
            return -5, no_data

        response_data = response[2: 2 + responseLength]
        

        return 1, response_data

    def felica_RequestService(self, nodeCodeList: List[int]) -> (int, List[int]):
        """
            Sends FeliCa Request Service command

            :param  nodeCodeList:      Node codes(Big Endian)
            :returns:   (status, keyVersions)
                        status      1: Success, < 0: error
                        keyVersions Key Version of each Node (Big Endian)
        """
        no_data = []
        numNode = len(nodeCodeList)
        if (numNode > FELICA_REQ_SERVICE_MAX_NODE_NUM):
            DMSG("numNode is too large\n")
            return -1, no_data

        cmd = bytearray([FELICA_CMD_REQUEST_SERVICE]) + self._felicaIDm[:8] + bytearray([numNode])
        for i in range(numNode):
            cmd.append(nodeCodeList[i] & 0xFF)
            cmd.append((nodeCodeList[i] >> 8) & 0xff)

        status, response = self.felica_SendCommand(cmd)
        if (status != 1):
            DMSG("Request Service command failed\n")
            return -2, no_data

        # length check
        responseLength = len(response)
        if (responseLength != 10 + 2 * numNode):
            DMSG("Request Service command failed (wrong response length)\n")
            return -3, no_data

        keyVersions = []
        for i in range(numNode):
            keyVersions.append(response[10 + i * 2] + (response[10 + i * 2 + 1] << 8))

        return 1, keyVersions

    def felica_RequestResponse(self) -> (int, int):
        """
        Sends FeliCa Request Response command

        :returns:     (status, mode)
                    status  1: Success, < 0: error
                    mode    Current Mode of the card
        """

        cmd = bytearray([FELICA_CMD_REQUEST_RESPONSE]) + self._felicaIDm[:8]

        status, response = self.felica_SendCommand(cmd)
        responseLength = len(response)
        if (status != 1):
            DMSG("Request Response command failed\n")
            return -1, -1

        # length check
        if (responseLength != 10):
            DMSG("Request Response command failed (wrong response length)\n")
            return -2, -1

        mode = response[9]
        return 1, mode

    def felica_ReadWithoutEncryption(self, serviceCodeList: List[int], blockList: List[int]) -> (int, List[bytearray]):

        """
            Sends FeliCa Read Without Encryption command

            :param  serviceCodeList:    Service Code List (Big Endian)
            :param  blockList:          Block List (Big Endian, This API only accepts 2-byte block list element)
            :returns:       (status, blockData)
                              status    1: Success, < 0: error
                              blockData Block Data
        """
        no_data = []
        numService =  len(serviceCodeList)
        if (numService > FELICA_READ_MAX_SERVICE_NUM):
            DMSG("numService is too large\n")
            return -1, no_data

        numBlock = len(blockList)
        if (numBlock > FELICA_READ_MAX_BLOCK_NUM):
            DMSG("numBlock is too large\n")
            return -2, no_data

        cmd = bytearray([FELICA_CMD_READ_WITHOUT_ENCRYPTION]) + self._felicaIDm[:8] + bytearray([numService])
        for i in range(numService):
            cmd.append(serviceCodeList[i] & 0xFF)
            cmd.append((serviceCodeList[i] >> 8) & 0xff)

        cmd.append(numBlock)
        for i in range(numBlock):
            cmd.append((blockList[i] >> 8) & 0xFF)
            cmd.append(blockList[i] & 0xff)

        status, response = self.felica_SendCommand(cmd)
        if (status != 1):
            DMSG("Read Without Encryption command failed\n")
            return -3, no_data


        # length check
        responseLength = len(response)
        if (responseLength != 12 + 16 * numBlock):
            DMSG("Read Without Encryption command failed (wrong response length)\n")
            return -4, no_data

        # status flag check
        if (response[9] != 0 or response[10] != 0):
            DMSG("Read Without Encryption command failed (Status Flag: ")
            DMSG_HEX(response[9])
            DMSG_HEX(response[10])
            DMSG(")\n")
            return -5, no_data

        k = 12
        blockData = []
        for i in range(numBlock):
            start = 12+ i * 16
            blockData.append(response[start: start + 16])

        return 1, blockData

    def felica_WriteWithoutEncryption(self, serviceCodeList: List[int], blockList: List[int], blockData: List[bytearray]) -> int:

        """
            Sends FeliCa Write Without Encryption command

            :param  serviceCodeList:    Service Code List (Big Endian)
            :param  blockList:          Block List (Big Endian, This API only accepts 2-byte block list element)
            :returns:       status    1: Success, < 0: error
        """
        numService, numBlock = len(serviceCodeList), len(blockList)
        if (numService > FELICA_WRITE_MAX_SERVICE_NUM):
            DMSG("numService is too large\n")
            return -1

        if (numBlock > FELICA_WRITE_MAX_BLOCK_NUM):
            DMSG("numBlock is too large\n")
            return -2

        cmd = bytearray([FELICA_CMD_WRITE_WITHOUT_ENCRYPTION]) + self._felicaIDm[:8] + bytearray([numService])
        for i in range(numService):
            cmd.append(serviceCodeList[i] & 0xFF)
            cmd.append((serviceCodeList[i] >> 8) & 0xff)

        cmd.append(numBlock)
        for i in range(numBlock):
            cmd.append((blockList[i] >> 8) & 0xFF)
            cmd.append(blockList[i] & 0xff)

        for i in range(numBlock):
            for k in range(16):
                cmd.append(blockData[i][k])

        status, response = self.felica_SendCommand(cmd)
        responseLength = len(response)
        if (status != 1):
            DMSG("Write Without Encryption command failed\n")
            return -3

        # length check
        if (responseLength != 11):
            DMSG("Write Without Encryption command failed (wrong response length)\n")
            return -4

        # status flag check
        if (response[9] != 0 or response[10] != 0):
            DMSG("Write Without Encryption command failed (Status Flag: ")
            DMSG_HEX(response[9])
            DMSG_HEX(response[10])
            DMSG(")\n")
            return -5

        return 1

    def felica_RequestSystemCode(self) -> (int, List[int]):
        """
        Sends FeliCa Request System Code command

        :returns:   (status, systemCodeList)
                    status          1: Success, < 0: error
                    systemCodeList  System Code list (Array length should longer than 16)

         """

        cmd = bytearray([FELICA_CMD_REQUEST_SYSTEM_CODE]) + self._felicaIDm[:8]

        status, response = self.felica_SendCommand(cmd)
        responseLength = len(response)
        if (status != 1):
            DMSG("Request System Code command failed\n")
            return -1, []

        numSystemCode = response[9]

        # length check
        if (responseLength < 10 + 2 * numSystemCode):
            DMSG("Request System Code command failed (wrong response length)\n")
            return -2, []

        systemCodeList = []
        for i in range(numSystemCode):
            systemCodeList.append((response[10 + i * 2] << 8) + response[10 + i * 2 + 1])

        return 1, systemCodeList

    # ************************************************************************
    # !
    
    # ************************************************************************
    def felica_Release(self) -> int:
        """
        Release FeliCa card
        :returns:   1: Success, < 0: error
        """
    
        # InRelease
        header = bytearray([
            PN532_COMMAND_INRELEASE,
            0x00,  # All target
        ])

        DMSG("Release all FeliCa target\n")

        if (self._interface.writeCommand(header)):
            DMSG("No ACK\n")
            return -1  # no ACK

        # Wait card response
        frameLength, response = self._interface.readResponse()
        if (frameLength < 0):
            DMSG("Could not receive response\n")
            return -2


        # Check status (response[0])
        if ((response[0] & 0x3F)!=0):
            DMSG("Status code indicates an error: ")
            DMSG_HEX(response[7])
            DMSG("\n")
            return -3

        return 1
