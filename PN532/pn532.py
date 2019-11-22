"""
    @file     PN532.cpp
    @author   Adafruit Industries & Seeed Studio
    @license  BSD

"""
from typing import List

from PN532.pn532Interface import pn532Interface, PN532_TIMEOUT

# PN532 Commands
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


PN532_MIFARE_ISO14443A              = (0x00)

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


DEBUG = False

def DMSG(msg):
    if DEBUG:
        print(msg)

def DMSG_HEX(char):
    if DEBUG:
        print('%x' % char)


class pn532:
    def __init__(self, interface: pn532Interface):
        self._interface = interface

        self._uid = []  # ISO14443A uid
        self._uidLen = 0  # uid len
        self._key = []  # Mifare Classic key
        self.inListedTag = 0 # Tg number of inlisted tag.
        self._felicaIDm = [] # FeliCa IDm (NFCID2)
        self._felicaPMm = [] # FeliCa PMm (PAD)

        self.pn532_packetbuffer = []
    

    def begin(self):
        """
        Setups the HW
        """
        self._interface.begin()
        self._interface.wakeup()

    def PrintHex(self, data: str, numBytes: int):
        """
            Prints a hexadecimal value in plain characters
    
            @param  data      Pointer to the uint8_t data
            @param  numBytes  Data length in bytes
        """
        for i in range(numBytes):
            print(" :X".format(data[i]))
        print("\n")

    def PrintHexChar(self, data: str, numBytes: int):
        """
        @brief  Prints a hexadecimal value in plain characters, along with
                the char equivalents in the following format

                00 00 00 00 00 00  ......

        @param  data      Pointer to the data
        @param  numBytes  Data length in bytes
        """    
        for i in range(numBytes):
            print(" {:2X}".format(data[i]))
        
        print("    ")
        for i in range(numBytes):
            c = data[i]
            if (c <= 0x1f or c > 0x7f):
                print(".")
            else:
                print("%c" % c)
            
            print("\n")

    def getBuffer(self) -> List[int]: 
        return self.pn532_packetbuffer

    def getFirmwareVersion(self) -> int:
        """
        @brief  Checks the firmware version of the PN5xx chip

        @returns  The chip's firmware version and ID
        """
        self.pn532_packetbuffer[0] = PN532_COMMAND_GETFIRMWAREVERSION

        if (self._interface.writeCommand(self.pn532_packetbuffer, 1)):
            return 0

        # read data packet
        status = self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer))
        if (0 > status):
            return 0

        response = self.pn532_packetbuffer[0]
        response <<= 8
        response |= self.pn532_packetbuffer[1]
        response <<= 8
        response |= self.pn532_packetbuffer[2]
        response <<= 8
        response |= self.pn532_packetbuffer[3]

        return response


    def readRegister(self, reg: int) -> int:
        """
        @brief  Read a PN532 register.

        @param  reg  the 16-bit register address.

        @returns  The register value.
        """
        self.pn532_packetbuffer[0] = PN532_COMMAND_READREGISTER
        self.pn532_packetbuffer[1] = (reg >> 8) & 0xFF
        self.pn532_packetbuffer[2] = reg & 0xFF

        if (self._interface.writeCommand(self.pn532_packetbuffer, 3)):
            return 0

        # read data packet
        status = self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer))
        if (0 > status):
            return 0

        response = self.pn532_packetbuffer[0]

        return response

    def writeRegister(self, reg: int, val: int) -> int:
        """
        @brief  Write to a PN532 register.

        @param  reg  the 16-bit register address.
        @param  val  the 8-bit value to write.

        @returns  0 for failure, 1 for success.
        """
        self.pn532_packetbuffer[0] = PN532_COMMAND_WRITEREGISTER
        self.pn532_packetbuffer[1] = (reg >> 8) & 0xFF
        self.pn532_packetbuffer[2] = reg & 0xFF
        self.pn532_packetbuffer[3] = val


        if (self._interface.writeCommand(self.pn532_packetbuffer, 4)):
            return 0
        

        # read data packet
        status = self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer))
        if (0 > status):
            return 0
        

        return 1

    def writeGPIO(self,  pinstate: int) -> bool:
        """
        Writes an 8-bit value that sets the state of the PN532's GPIO pins

        @warning This function is provided exclusively for board testing and
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

        @returns 1 if everything executed properly, 0 for an error
        """
    
        # Make sure pinstate does not try to toggle P32 or P34
        pinstate |= (1 << PN532_GPIO_P32) | (1 << PN532_GPIO_P34)

        # Fill command buffer
        self.pn532_packetbuffer[0] = PN532_COMMAND_WRITEGPIO
        self.pn532_packetbuffer[1] = PN532_GPIO_VALIDATIONBIT | pinstate  # P3 Pins
        self.pn532_packetbuffer[2] = 0x00    # P7 GPIO Pins (not used ... taken by I2C)

        DMSG("Writing P3 GPIO: ")
        DMSG_HEX(self.pn532_packetbuffer[1])
        DMSG("\n")

        # Send the WRITEGPIO command (0x0E)
        if (self._interface.writeCommand(self.pn532_packetbuffer, 3)):
            return False

        return (0 < self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer)))
    

    def readGPIO(self) -> int:
        """
            Reads the state of the PN532's GPIO pins

            :returns An 8-bit value containing the pin state where:

                 pinState[0]  = P30
                 pinState[1]  = P31
                 pinState[2]  = P32
                 pinState[3]  = P33
                 pinState[4]  = P34
                 pinState[5]  = P35 
        """
    
        self.pn532_packetbuffer[0] = PN532_COMMAND_READGPIO

        # Send the READGPIO command (0x0C)
        if (self._interface.writeCommand(self.pn532_packetbuffer, 1)):
            return 0x0

        self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer))
        # READGPIO response without prefix and suffix should be in the following format:
        # 
        #   byte            Description
        #   -------------   ------------------------------------------
        #   b0              P3 GPIO Pins
        #   b1              P7 GPIO Pins (not used ... taken by I2C)
        #   b2              Interface Mode Pins (not used ... bus select pins)

        DMSG("P3 GPIO: ") 
        DMSG_HEX(self.pn532_packetbuffer[7])
        DMSG("P7 GPIO: ") 
        DMSG_HEX(self.pn532_packetbuffer[8])
        DMSG("I0I1 GPIO: ") 
        DMSG_HEX(self.pn532_packetbuffer[9])
        DMSG("\n")

        return self.pn532_packetbuffer[0]
    

    def SAMConfig(self) -> bool:
        """
        @brief  Configures the SAM (Secure Access Module) 
        """
    
        self.pn532_packetbuffer[0] = PN532_COMMAND_SAMCONFIGURATION
        self.pn532_packetbuffer[1] = 0x01 # normal mode
        self.pn532_packetbuffer[2] = 0x14 # timeout 50ms * 20 = 1 second
        self.pn532_packetbuffer[3] = 0x01 # use IRQ pin!

        DMSG("SAMConfig\n")

        if (self._interface.writeCommand(self.pn532_packetbuffer, 4)):
            return False

        return (0 < self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer)))
    

    def setPassiveActivationRetries(self, maxRetries: int) -> bool:
        """
        Sets the MxRtyPassiveActivation uint8_t of the RFConfiguration register

        @param  maxRetries    0xFF to wait forever, 0x00..0xFE to timeout
                              after mxRetries

        @returns 1 if everything executed properly, 0 for an error
        """
    
        self.pn532_packetbuffer[0] = PN532_COMMAND_RFCONFIGURATION
        self.pn532_packetbuffer[1] = 5    # Config item 5 (MaxRetries)
        self.pn532_packetbuffer[2] = 0xFF # MxRtyATR (default = 0xFF)
        self.pn532_packetbuffer[3] = 0x01 # MxRtyPSL (default = 0x01)
        self.pn532_packetbuffer[4] = maxRetries

        if (self._interface.writeCommand(self.pn532_packetbuffer, 5)):
            return False  # no ACK

        return (0 < self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer)))
    

    def setRFField(self, autoRFCA: int, rFOnOff: int) -> bool:
        """
        Sets the RFon/off uint8_t of the RFConfiguration register

        @param  autoRFCA    0x00 No check of the external field before
                            activation

                            0x02 Check the external field before
                            activation

        @param  rFOnOff     0x00 Switch the RF field off, 0x01 switch the RF
                            field on

        @returns    1 if everything executed properly, 0 for an error
        """
    
        self.pn532_packetbuffer[0] = PN532_COMMAND_RFCONFIGURATION
        self.pn532_packetbuffer[1] = 1
        self.pn532_packetbuffer[2] = 0x00 | autoRFCA | rFOnOff

        if (self._interface.writeCommand(self.pn532_packetbuffer, 3)) :
            return False  # command failed
        

        return (0 < self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer)))
    

    # **** ISO14443A Commands *****

    def readPassiveTargetID(self, cardbaudrate: int, uid: str, uidLength: int, timeout: int, inlist: bool) -> bool:
        """
        Waits for an ISO14443A target to enter the field

        @param  cardBaudRate  Baud rate of the card
        @param  uid           Pointer to the array that will be populated
                              with the card's UID (up to 7 bytes)
        @param  uidLength     Pointer to the variable that will hold the
                              length of the card's UID.
        @param  timeout       The number of tries before timing out
        @param  inlist        If set to True, the card will be inlisted

        @returns 1 if everything executed properly, 0 for an error
        """
        self.pn532_packetbuffer[0] = PN532_COMMAND_INLISTPASSIVETARGET
        self.pn532_packetbuffer[1] = 1  # max 1 cards at once (we can set this to 2 later)
        self.pn532_packetbuffer[2] = cardbaudrate

        if (self._interface.writeCommand(self.pn532_packetbuffer, 3)) :
            return False  # command failed
        

        # read data packet
        if (self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer), timeout) < 0): 
            return False
        

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

        if (self.pn532_packetbuffer[0] != 1):
            return False

        sens_res = self.pn532_packetbuffer[2]
        sens_res <<= 8
        sens_res |= self.pn532_packetbuffer[3]

        DMSG("ATQA: 0x")
        DMSG_HEX(sens_res)
        DMSG("SAK: 0x")
        DMSG_HEX(self.pn532_packetbuffer[4])
        DMSG("\n")

        # Card appears to be Mifare Classic 
        uidLength = self.pn532_packetbuffer[5]

        for i in range(self.pn532_packetbuffer[5]):
            uid[i] = self.pn532_packetbuffer[6 + i]
        

        if (inlist) :
            self.inListedTag = self.pn532_packetbuffer[1]
        
        return True
    


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
    

    def mifareclassic_AuthenticateBlock(self, uid: str, uidLen: int, blockNumber: int, keyNumber: int, keyData: str) -> int:
        """
                Tries to authenticate a block of memory on a MIFARE card using the
        INDATAEXCHANGE command.  See section 7.3.8 of the PN532 User Manual
        for more information on sending MIFARE and other commands.

        @param  uid           Pointer to a byte array containing the card UID
        @param  uidLen        The length (in bytes) of the card's UID (Should
                              be 4 for MIFARE Classic)
        @param  blockNumber   The block number to authenticate.  (0..63 for
                              1KB cards, and 0..255 for 4KB cards).
        @param  keyNumber     Which key type to use during authentication
                              (0 = MIFARE_CMD_AUTH_A, 1 = MIFARE_CMD_AUTH_B)
        @param  keyData       Pointer to a byte array containing the 6 bytes
                              key value

        @returns 1 if everything executed properly, 0 for an error
        """
    
        # Hang on to the key and uid data
        self._key = keyData
        self._uid = uid
        self._uidLen = uidLen

        # Prepare the authentication command #
        self.pn532_packetbuffer = [PN532_COMMAND_INDATAEXCHANGE, 1,
                                   MIFARE_CMD_AUTH_B if keyNumber else MIFARE_CMD_AUTH_A, blockNumber]
        self.pn532_packetbuffer.append(self._key[:6])
        for i in range(self._uidLen):
            self.pn532_packetbuffer[10 + i] = self._uid[i]              #  4 bytes card ID 
        

        if (self._interface.writeCommand(self.pn532_packetbuffer, 10 + self._uidLen)):
            return 0

        # Read the response packet
        self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer))

        # Check if the response is valid and we are authenticated???
        # for an auth success it should be bytes 5-7: 0xD5 0x41 0x00
        # Mifare auth error is technically byte 7: 0x14 but anything other and 0x00 is not good
        if (self.pn532_packetbuffer[0] != 0x00):
            DMSG("Authentication failed\n")
            return 0
        

        return 1
    

    def mifareclassic_ReadDataBlock (self, blockNumber: int, data: str) -> int:
        """
        Tries to read an entire 16-bytes data block at the specified block
        address.

        @param  blockNumber   The block number to authenticate.  (0..63 for
                              1KB cards, and 0..255 for 4KB cards).
        @param  data          Pointer to the byte array that will hold the
                              retrieved data (if any)

        @returns 1 if everything executed properly, 0 for an error
        """
    
        DMSG("Trying to read 16 bytes from block ")
        DMSG(blockNumber)

        #  Prepare the command 
        self.pn532_packetbuffer[0] = PN532_COMMAND_INDATAEXCHANGE
        self.pn532_packetbuffer[1] = 1                      #  Card number 
        self.pn532_packetbuffer[2] = MIFARE_CMD_READ        #  Mifare Read command = 0x30 
        self.pn532_packetbuffer[3] = blockNumber            #  Block Number (0..63 for 1K, 0..255 for 4K) 

        #  Send the command 
        if (self._interface.writeCommand(self.pn532_packetbuffer, 4)):
            return 0
        

        #  Read the response packet 
        self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer))

        #  If byte 8 isn't 0x00 we probably have an error 
        if (self.pn532_packetbuffer[0] != 0x00):
            return 0
        

        #  Copy the 16 data bytes to the output buffer        
        #  Block content starts at byte 9 of a valid response
        data = {self.pn532_packetbuffer[1:17]}

        return 1
    

    def mifareclassic_WriteDataBlock (self, blockNumber: int, data: str) -> int:
        """
                Tries to write an entire 16-bytes data block at the specified block
        address.

        @param  blockNumber   The block number to authenticate.  (0..63 for
                              1KB cards, and 0..255 for 4KB cards).
        @param  data          The byte array that contains the data to write.

        @returns 1 if everything executed properly, 0 for an error
        """
    
    
        #  Prepare the first command
        self.pn532_packetbuffer = [PN532_COMMAND_INDATAEXCHANGE, 1, MIFARE_CMD_WRITE, blockNumber]
        self.pn532_packetbuffer.append(data[:16])

        #  Send the command 
        if (self._interface.writeCommand(self.pn532_packetbuffer, 20)): 
            return 0
        

        #  Read the response packet 
        return (0 < self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer)))
    

    def mifareclassic_FormatNDEF (self) -> int:
        """
                Formats a Mifare Classic card to store NDEF Records

        @returns 1 if everything executed properly, 0 for an error
        """
    
        sectorbuffer1 = [0x14, 0x01, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1]
        sectorbuffer2 = [0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1]
        sectorbuffer3 = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0x78, 0x77, 0x88, 0xC1, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        # Note 0xA0 0xA1 0xA2 0xA3 0xA4 0xA5 must be used for key A
        # for the MAD sector in NDEF records (sector 0)

        # Write block 1 and 2 to the card
        if (not (self.mifareclassic_WriteDataBlock(1, sectorbuffer1))):
            return 0
        if (not (self.mifareclassic_WriteDataBlock(2, sectorbuffer2))):
            return 0
        # Write key A and access rights card
        if (not (self.mifareclassic_WriteDataBlock(3, sectorbuffer3))):
            return 0

        # Seems that everything was OK (?!)
        return 1


    def mifareclassic_WriteNDEFURI (self, sectorNumber: int, uriIdentifier: int, url: str, x) -> int:
        """
        Writes an NDEF URI Record to the specified sector (1..15)

        Note that this function assumes that the Mifare Classic card is
        already formatted to work as an "NFC Forum Tag" and uses a MAD1
        file system.  You can use the NXP TagWriter app on Android to
        properly format cards for this.

        :param  sectorNumber:  The sector that the URI record should be written
                              to (can be 1..15 for a 1K card)
        :param  uriIdentifier: The uri identifier code (0 = none, 0x01 =
                              "http:#www.", etc.)
        :param  url_bytes:           The uri text to write (max 38 characters).

        :return: 1 if everything executed properly, 0 for an error
        """

        # Figure out how long the string is
        url_bytes = bytearray(url, 'ascii')
        length = len(url_bytes)

        # Make sure we're within a 1K limit for the sector number
        if ((sectorNumber < 1) or (sectorNumber > 15)):
            return 0

        # Make sure the URI payload is between 1 and 38 chars
        if ((length < 1) or (length > 38)):
            return 0

        # Note 0xD3 0xF7 0xD3 0xF7 0xD3 0xF7 must be used for key A
        # in NDEF records

        # Setup the sector buffer (w/pre-formatted TLV wrapper and NDEF message)
        sectorbuffer1 = bytearray([0x00, 0x00, 0x03, length + 5, 0xD1, 0x01, length + 1, 0x55, uriIdentifier, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        sectorbuffer2 = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        sectorbuffer3 = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        sectorbuffer4 = bytearray([0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7, 0x7F, 0x07, 0x88, 0x40, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
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
            sectorbuffer2 = url_bytes[length - 7:] + sectorbuffer2[length - 7:]
            sectorbuffer2[length - 7] = 0xFE
        elif (length == 23):
            # 0xFE needs to be wrapped around to final block
            sectorbuffer1 = sectorbuffer1[:9] + url_bytes[:7] + sectorbuffer1[9 + 7:]
            sectorbuffer2 = url_bytes[length - 7:]
            sectorbuffer3[0] = 0xFE
        else:
            # Url fits in three blocks
            sectorbuffer1 = sectorbuffer1[:9] + url_bytes[:7] + sectorbuffer1[9 + 7:]
            sectorbuffer2 = url_bytes[7:23]
            sectorbuffer3 = url_bytes[23:] + sectorbuffer3[length - 23:]
            sectorbuffer3[length - 23] = 0xFE
        

        # Now write all three blocks back to the card
        if (not (self.mifareclassic_WriteDataBlock(sectorNumber * 4, sectorbuffer1))):
            return 0
        if (not (self.mifareclassic_WriteDataBlock((sectorNumber * 4) + 1, sectorbuffer2))):
            return 0
        if (not (self.mifareclassic_WriteDataBlock((sectorNumber * 4) + 2, sectorbuffer3))):
            return 0
        if (not (self.mifareclassic_WriteDataBlock((sectorNumber * 4) + 3, sectorbuffer4))):
            return 0

        # Seems that everything was OK (?!)
        return 1
    

    # **** Mifare Ultralight Functions *****

    def mifareultralight_ReadPage(self, page: int, buffer: str) -> int:
        """
                Tries to read an entire 4-bytes page at the specified address.

        @param  page        The page number (0..63 in most cases)
        @param  buffer      Pointer to the byte array that will hold the
                            retrieved data (if any)
        """
    
        #  Prepare the command 
        self.pn532_packetbuffer[0] = PN532_COMMAND_INDATAEXCHANGE
        self.pn532_packetbuffer[1] = 1                   #  Card number 
        self.pn532_packetbuffer[2] = MIFARE_CMD_READ     #  Mifare Read command = 0x30 
        self.pn532_packetbuffer[3] = page                #  Page Number (0..63 in most cases) 

        #  Send the command 
        if (self._interface.writeCommand(self.pn532_packetbuffer, 4)):
            return 0
        

        #  Read the response packet 
        self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer))

        #  If byte 8 isn't 0x00 we probably have an error 
        if (self.pn532_packetbuffer[0] == 0x00) :
            #  Copy the 4 data bytes to the output buffer         
            #  Block content starts at byte 9 of a valid response 
            #  Note that the command actually reads 16 bytes or 4  
            #  pages at a time ... we simply discard the last 12  
            #  bytes                                              
            buffer = self.pn532_packetbuffer[1:5]
        else:
            return 0
        

        # Return OK signal
        return 1
    

    def mifareultralight_WritePage(self, page: int, buffer: str) -> int:
        """
        Tries to write an entire 4-bytes data buffer at the specified page
        address.

        @param  page     The page number to write into.  (0..63).
        @param  buffer   The byte array that contains the data to write.

        @returns 1 if everything executed properly, 0 for an error
        """
    
        #  Prepare the first command 
        self.pn532_packetbuffer = [PN532_COMMAND_INDATAEXCHANGE, 1, MIFARE_CMD_WRITE_ULTRALIGHT, page]
        self.pn532_packetbuffer.append(buffer[:4])

        #  Send the command 
        if (self._interface.writeCommand(self.pn532_packetbuffer, 8)):
            return 0
        

        #  Read the response packet 
        return (0 < self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer)))
    

    def inDataExchange(self, send: str, sendLength: int, response: str, responseLength: str) -> bool:
        """
                @brief  Exchanges an APDU with the currently inlisted peer

        @param  send            Pointer to data to send
        @param  sendLength      Length of the data to send
        @param  response        Pointer to response data
        @param  responseLength  Pointer to the response data length
        """
    
        self.pn532_packetbuffer[0] = 0x40 # PN532_COMMAND_INDATAEXCHANGE
        self.pn532_packetbuffer[1] = self.inListedTag

        if (self._interface.writeCommand(self.pn532_packetbuffer, 2, send, sendLength)):
            return False
        

        status = self._interface.readResponse(response, responseLength, 1000)
        if (status < 0):
            return False
        

        if ((response[0] & 0x3f) != 0):
            DMSG("Status code indicates an error\n")
            return False
        

        length = status
        length -= 1

        if (length > responseLength):
            length = responseLength # silent truncation...
        

        for i in range(length):
            response[i] = response[i + 1]
        
        responseLength = length

        return True
    

    def inListPassiveTarget(self) -> bool:
        """
            # !
        @brief  'InLists' a passive target. PN532 acting as reader/initiator,
                peer acting as card/responder.
        """
    
        self.pn532_packetbuffer[0] = PN532_COMMAND_INLISTPASSIVETARGET
        self.pn532_packetbuffer[1] = 1
        self.pn532_packetbuffer[2] = 0

        DMSG("inList passive target\n")

        if (self._interface.writeCommand(self.pn532_packetbuffer, 3)):
            return False
        

        status = self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer), 30000)
        if (status < 0) :
            return False
        

        if (self.pn532_packetbuffer[0] != 1):
            return False
        

        self.inListedTag = self.pn532_packetbuffer[1]

        return True
    

    def tgInitAsTarget(self, command: str, len: int, timeout: int) -> int:

        status = self._interface.writeCommand(command, len)
        if (status < 0):
            return -1
        

        status = self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer), timeout)
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

        command = [
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
            0x00]

        return self.tgInitAsTarget(command, len(command), timeout)
    

    def tgGetData(self, buf: str, len: int) -> int:
    
        buf[0] = PN532_COMMAND_TGGETDATA

        if (self._interface.writeCommand(buf, 1)):
            return -1
        

        status = self._interface.readResponse(buf, len, 3000)
        if (0 >= status):
            return status
        

        length = status - 1


        if (buf[0] != 0):
            DMSG("status is not ok\n")
            return -5
        

        for i in range(length):
            buf[i] = buf[i + 1]
        

        return length
    

    def tgSetData(self, header: str, hlen: int, body: str, blen: int) -> bool:
    
        if (hlen > (len(self.pn532_packetbuffer) - 1)):
            if ((body != 0) or (header == self.pn532_packetbuffer)) :
                DMSG("tgSetData:buffer too small\n")
                return False
            

            self.pn532_packetbuffer[0] = PN532_COMMAND_TGSETDATA
            if (self._interface.writeCommand(self.pn532_packetbuffer, 1, header, hlen)):
                return False
            
        else :
            for i in range(hlen).__reversed__():
                self.pn532_packetbuffer[i + 1] = header[i]
            
            self.pn532_packetbuffer[0] = PN532_COMMAND_TGSETDATA

            if (self._interface.writeCommand(self.pn532_packetbuffer, hlen + 1, body, blen)):
                return False
            
        

        if (0 > self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer), 3000)):
            return False
        

        if (0 != self.pn532_packetbuffer[0]):
            return False
        

        return True
    

    def inRelease(self, relevantTarget: str) -> int:

        self.pn532_packetbuffer[0] = PN532_COMMAND_INRELEASE
        self.pn532_packetbuffer[1] = relevantTarget

        if (self._interface.writeCommand(self.pn532_packetbuffer, 2)):
            return 0
        

        # read data packet
        return self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer))

    def felica_Polling(self, systemCode: int, requestCode: int, idm: str, pmm: str, systemCodeResponse: str,
                       timeout: int) -> int:
        """
                @brief  Poll FeliCa card. PN532 acting as reader/initiator,
                    peer acting as card/responder.
            @param[in]  systemCode             Designation of System Code. When sending FFFFh as System Code,
                                               all FeliCa cards can return response.
            @param[in]  requestCode            Designation of Request Data as follows:
                                                 00h: No Request
                                                 01h: System Code request (to acquire System Code of the card)
                                                 02h: Communication perfomance request
            @param[out] idm                    IDm of the card (8 bytes)
            @param[out] pmm                    PMm of the card (8 bytes)
            @param[out] systemCodeResponse     System Code of the card (Optional, 2bytes)
            @return                            = 1: A FeliCa card has detected
                                               = 0: No card has detected
                                               < 0: error
        """
        self.pn532_packetbuffer[0] = PN532_COMMAND_INLISTPASSIVETARGET
        self.pn532_packetbuffer[1] = 1
        self.pn532_packetbuffer[2] = 1
        self.pn532_packetbuffer[3] = FELICA_CMD_POLLING
        self.pn532_packetbuffer[4] = (systemCode >> 8) & 0xFF
        self.pn532_packetbuffer[5] = systemCode & 0xFF
        self.pn532_packetbuffer[6] = requestCode
        self.pn532_packetbuffer[7] = 0

        if (self._interface.writeCommand(self.pn532_packetbuffer, 8)):
            DMSG("Could not send Polling command\n")
            return -1

        status = self._interface.readResponse(self.pn532_packetbuffer, 22, timeout)
        if (status < 0):
            DMSG("Could not receive response\n")
            return -2

        # Check NbTg (pn532_packetbuffer[7])
        if (self.pn532_packetbuffer[0] == 0):
            DMSG("No card had detected\n")
            return 0
        elif (self.pn532_packetbuffer[0] != 1):
            DMSG("Unhandled number of targets inlisted. NbTg: ")
            DMSG_HEX(self.pn532_packetbuffer[7])
            DMSG("\n")
            return -3

        self.inListedTag = self.pn532_packetbuffer[1]
        DMSG("Tag number: ")
        DMSG_HEX(self.pn532_packetbuffer[1])
        DMSG("\n")

        # length check
        responseLength = self.pn532_packetbuffer[2]
        if (responseLength != 18 and responseLength != 20):
            DMSG("Wrong response length\n")
            return -4

        i = 0
        for i in range(8):
            idm[i] = self.pn532_packetbuffer[4 + i]
            self._felicaIDm[i] = self.pn532_packetbuffer[4 + i]
            pmm[i] = self.pn532_packetbuffer[12 + i]
            self._felicaPMm[i] = self.pn532_packetbuffer[12 + i]

        if (responseLength == 20):
            systemCodeResponse = ((self.pn532_packetbuffer[20] << 8) + self.pn532_packetbuffer[21]) & 0xFF

        return 1

    def felica_SendCommand(self, command: str, commandlength: int, response: str, responseLength: int) -> int:
        """
                @brief  Sends FeliCa command to the currently inlisted peer

            @param[in]  command         FeliCa command packet. (e.g. 00 FF FF 00 00  for Polling command)
            @param[in]  commandlength   Length of the FeliCa command packet. (e.g. 0x05 for above Polling command )
            @param[out] response        FeliCa response packet. (e.g. 01 NFCID2(8 bytes) PAD(8 bytes)  for Polling response)
            @param[out] responselength  Length of the FeliCa response packet. (e.g. 0x11 for above Polling command )
            @return                          = 1: Success
                                             < 0: error
        """

        if (commandlength > 0xFE):
            DMSG("Command length too long\n")
            return -1

        self.pn532_packetbuffer[0] = 0x40  # PN532_COMMAND_INDATAEXCHANGE
        self.pn532_packetbuffer[1] = self.inListedTag
        self.pn532_packetbuffer[2] = commandlength + 1

        if (self._interface.writeCommand(self.pn532_packetbuffer, 3, command, commandlength)):
            DMSG("Could not send FeliCa command\n")
            return -2

        # Wait card response
        status = self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer), 200)
        if (status < 0):
            DMSG("Could not receive response\n")
            return -3

        # Check status (pn532_packetbuffer[0])
        if ((self.pn532_packetbuffer[0] & 0x3F) != 0):
            DMSG("Status code indicates an error: ")
            DMSG_HEX(self.pn532_packetbuffer[0])
            DMSG("\n")
            return -4

        # length check
        responseLength = self.pn532_packetbuffer[1] - 1
        if ((status - 2) !=  responseLength):
            DMSG("Wrong response length\n")
            return -5

        response = self.pn532_packetbuffer[2: 2 + responseLength]
        

        return 1

    def felica_RequestService(self, numNode: int, nodeCodeList: str, keyVersions: str) -> int:
        """
            @brief  Sends FeliCa Request Service command

            @param[in]  numNode           length of the nodeCodeList
            @param[in]  nodeCodeList      Node codes(Big Endian)
            @param[out] keyVersions       Key Version of each Node (Big Endian)
            @return                          = 1: Success
                                             < 0: error
        """

        if (numNode > FELICA_REQ_SERVICE_MAX_NODE_NUM):
            DMSG("numNode is too large\n")
            return -1

        cmdLen = 1 + 8 + 1 + 2 * numNode
        cmd = [FELICA_CMD_REQUEST_SERVICE] + self._felicaIDm[:8] + [numNode]
        for i in range(numNode):
            cmd.append(nodeCodeList[i] & 0xFF)
            cmd.append((nodeCodeList[i] >> 8) & 0xff)

        response = []
        responseLength = 0

        if (self.felica_SendCommand(cmd, cmdLen, response, responseLength) != 1):
            DMSG("Request Service command failed\n")
            return -2

        # length check
        if (responseLength != 10 + 2 * numNode):
            DMSG("Request Service command failed (wrong response length)\n")
            return -3

        for i in range(numNode):
            keyVersions[i] = (response[10 + i * 2] + (response[10 + i * 2 + 1] << 8)) & 0xFF

        return 1

    def felica_RequestResponse(self, mode: str) -> int:
        """
        @brief  Sends FeliCa Request Service command

        @param[out]  mode         Current Mode of the card
        @return                   = 1: Success
                                  < 0: error
        """

        cmd = [FELICA_CMD_REQUEST_RESPONSE] + self._felicaIDm[:8]

        response = []
        responseLength = 0
        if (self.felica_SendCommand(cmd, 9, response, responseLength) != 1):
            DMSG("Request Response command failed\n")
            return -1

        # length check
        if (responseLength != 10):
            DMSG("Request Response command failed (wrong response length)\n")
            return -2

        mode = response[9]
        return 1

    def felica_ReadWithoutEncryption(self, numService: int, serviceCodeList: str, numBlock: int, blockList: str,
                                     blockData: str) -> int:

        """
            @brief  Sends FeliCa Read Without Encryption command

            @param[in]  numService         Length of the serviceCodeList
            @param[in]  serviceCodeList    Service Code List (Big Endian)
            @param[in]  numBlock           Length of the blockList
            @param[in]  blockList          Block List (Big Endian, This API only accepts 2-byte block list element)
            @param[out] blockData          Block Data
            @return                        = 1: Success
                                           < 0: error
        """
        if (numService > FELICA_READ_MAX_SERVICE_NUM):
            DMSG("numService is too large\n")
            return -1

        if (numBlock > FELICA_READ_MAX_BLOCK_NUM):
            DMSG("numBlock is too large\n")
            return -2

        cmdLen = 1 + 8 + 1 + 2 * numService + 1 + 2 * numBlock
        cmd = [FELICA_CMD_READ_WITHOUT_ENCRYPTION] + self._felicaIDm[:8] + [numService]
        for i in range(numService):
            cmd.append(serviceCodeList[i] & 0xFF)
            cmd.append((serviceCodeList[i] >> 8) & 0xff)

        cmd.append(numBlock)
        for i in range(numBlock):
            cmd.append((blockList[i] >> 8) & 0xFF)
            cmd.append(blockList[i] & 0xff)

        response = []
        responseLength = 0
        if (self.felica_SendCommand(cmd, cmdLen, response, responseLength) != 1):
            DMSG("Read Without Encryption command failed\n")
            return -3


        # length check
        if (responseLength != 12 + 16 * numBlock):
            DMSG("Read Without Encryption command failed (wrong response length)\n")
            return -4

        # status flag check
        if (response[9] != 0 or response[10] != 0):
            DMSG("Read Without Encryption command failed (Status Flag: ")
            DMSG_HEX(self.pn532_packetbuffer[9])
            DMSG_HEX(self.pn532_packetbuffer[10])
            DMSG(")\n")
            return -5

        k = 12
        for i in range(numBlock):
            for j in range(8):
                blockData[i][j] = response[k]
                k += 1

        return 1



    def felica_WriteWithoutEncryption(self, numService: int, serviceCodeList: str, numBlock: int, blockList: str,
                                      blockData: str) -> int:

        """
                @brief  Sends FeliCa Write Without Encryption command

            @param[in]  numService         Length of the serviceCodeList
            @param[in]  serviceCodeList    Service Code List (Big Endian)
            @param[in]  numBlock           Length of the blockList
            @param[in]  blockList          Block List (Big Endian, This API only accepts 2-byte block list element)
            @param[in]  blockData          Block Data (each Block has 16 bytes)
            @return                        = 1: Success
                                           < 0: error
        """

        if (numService > FELICA_WRITE_MAX_SERVICE_NUM):
            DMSG("numService is too large\n")
            return -1

        if (numBlock > FELICA_WRITE_MAX_BLOCK_NUM):
            DMSG("numBlock is too large\n")
            return -2

        i, j , k = (0, 0, 0)
        cmdLen = 1 + 8 + 1 + 2 * numService + 1 + 2 * numBlock + 16 * numBlock
        cmd = [cmdLen]
        cmd.append(FELICA_CMD_WRITE_WITHOUT_ENCRYPTION)
        for i in range(8):
            cmd.append(self._felicaIDm[i])

        cmd.append(numService)
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

        response = []
        responseLength = 0
        if (self.felica_SendCommand(cmd, cmdLen, response, responseLength) != 1):
            DMSG("Write Without Encryption command failed\n")
            return -3


        # length check
        if (responseLength != 11):
            DMSG("Write Without Encryption command failed (wrong response length)\n")
            return -4

        # status flag check
        if (response[9] != 0 or response[10] != 0):
            DMSG("Write Without Encryption command failed (Status Flag: ")
            DMSG_HEX(self.pn532_packetbuffer[9])
            DMSG_HEX(self.pn532_packetbuffer[10])
            DMSG(")\n")
            return -5

        return 1
    

    def felica_RequestSystemCode(self, numSystemCode: str, systemCodeList:str) -> int:
        """
                @brief  Sends FeliCa Request System Code command

        @param[out] numSystemCode        Length of the systemCodeList
        @param[out] systemCodeList       System Code list (Array length should longer than 16)
        @return                          = 1: Success
                                         < 0: error
         """

        cmd = [FELICA_CMD_REQUEST_SYSTEM_CODE] + self._felicaIDm[:8]

        response = []
        responseLength = []
        if (self.felica_SendCommand(cmd, 9, response, responseLength) != 1):
            DMSG("Request System Code command failed\n")
            return -1

        numSystemCode = response[9]

        # length check
        if (responseLength < 10 + 2 * numSystemCode):
            DMSG("Request System Code command failed (wrong response length)\n")
            return -2

        i = 0
        for i in range(numSystemCode):
            systemCodeList[i] = ((response[10 + i * 2] << 8) + response[10 + i * 2 + 1]) & 0xFFFF

        return 1
    


    # ************************************************************************
    # !

    
    # ************************************************************************
    def felica_Release(self) -> int:
        """
                @brief  Release FeliCa card
        @return                          = 1: Success
                                         < 0: error
        """
    
        # InRelease
        self.pn532_packetbuffer[0] = PN532_COMMAND_INRELEASE
        self.pn532_packetbuffer[1] = 0x00   # All target
        DMSG("Release all FeliCa target\n")

        if (self._interface.writeCommand(self.pn532_packetbuffer, 2)):
            DMSG("No ACK\n")
            return -1  # no ACK


        # Wait card response
        frameLength = self._interface.readResponse(self.pn532_packetbuffer, len(self.pn532_packetbuffer), 1000)
        if (frameLength < 0):
            DMSG("Could not receive response\n")
            return -2


        # Check status (pn532_packetbuffer[0])
        if ((self.pn532_packetbuffer[0] & 0x3F)!=0):
            DMSG("Status code indicates an error: ")
            DMSG_HEX(self.pn532_packetbuffer[7])
            DMSG("\n")
            return -3


        return 1
    
