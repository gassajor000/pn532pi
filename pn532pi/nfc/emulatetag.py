"""
    @file     emulatetag.cpp
    @author   Armin Wieser
    @license  BSD
    """
from typing import Callable, Any

from pn532pi.nfc.pn532 import Pn532, PN532_COMMAND_TGINITASTARGET
from pn532pi.nfc.pn532_log import DMSG

NDEF_MAX_LENGTH = 128  # altough ndef can handle up to 0xfffe in size, arduino cannot.

MAX_TGREAD = True

# Command APDU
C_APDU_CLA = 0
C_APDU_INS = 1  # instruction
C_APDU_P1 = 2  # parameter 1
C_APDU_P2 = 3  # parameter 2
C_APDU_LC = 4  # length command
C_APDU_DATA = 5  # data

C_APDU_P1_SELECT_BY_ID = 0x00
C_APDU_P1_SELECT_BY_NAME = 0x04

# Response APDU
R_APDU_SW1_COMMAND_COMPLETE = 0x90
R_APDU_SW2_COMMAND_COMPLETE = 0x00

R_APDU_SW1_NDEF_TAG_NOT_FOUND = 0x6a
R_APDU_SW2_NDEF_TAG_NOT_FOUND = 0x82

R_APDU_SW1_FUNCTION_NOT_SUPPORTED = 0x6A
R_APDU_SW2_FUNCTION_NOT_SUPPORTED = 0x81

R_APDU_SW1_MEMORY_FAILURE = 0x65
R_APDU_SW2_MEMORY_FAILURE = 0x81

R_APDU_SW1_END_OF_FILE_BEFORE_REACHED_LE_BYTES = 0x62
R_APDU_SW2_END_OF_FILE_BEFORE_REACHED_LE_BYTES = 0x82

# ISO7816-4 commands
ISO7816_SELECT_FILE = 0xA4
ISO7816_READ_BINARY = 0xB0
ISO7816_UPDATE_BINARY = 0xD6

# Tag File
TAGFILE_NONE = 0
TAGFILE_CC = 1
TAGFILE_NDEF = 2

# Response Command
RESPCMD_COMMAND_COMPLETE = 0
RESPCMD_TAG_NOT_FOUND = 1
RESPCMD_FUNCTION_NOT_SUPPORTED = 2
RESPCMD_MEMORY_FAILURE = 3
RESPCMD_END_OF_FILE_BEFORE_REACHED_LE_BYTES = 4


class EmulateTag:
    def __init__(self, interface: Pn532):
        self.pn532 = interface
        self.uid = bytearray()
        self.tagWrittenByInitiator = False
        self.tagWriteable = True
        self.updateNdefCallback = None
        self.currentFile = TAGFILE_NONE
        self.ndef_file = bytearray()

    def init(self) -> bool:
        self.pn532.begin()
        return self.pn532.SAMConfig()

    def setNdefFile(self, ndef: bytearray):
        ndefLength = len(ndef)
        if (ndefLength > (NDEF_MAX_LENGTH - 2)):
            DMSG("ndef file too large (> NDEF_MAX_LENGHT -2) - aborting")
            return

        self.ndef_file = bytearray([ndefLength >> 8, ndefLength & 0xFF]) + ndef

    def setUid(self, uid: bytearray = bytearray()):
        self.uid = uid

    def getContent(self) -> (bytearray, int):
        """
        :return: (buf, len) content and length
        """
        # first 2 bytes = length
        length = (self.ndef_file[0] << 8) + self.ndef_file[1]
        return (self.ndef_file[2:], length)

    def writeOccured(self) -> bool:
        return self.tagWrittenByInitiator

    def setTagWriteable(self, setWriteable: bool):
        self.tagWriteable = setWriteable

    def getNdefMaxLength(self) -> int:
        return NDEF_MAX_LENGTH

    def attach(self, func: Callable[[bytearray], Any]):
        self.updateNdefCallback = func

    def emulate(self, tgInitAsTargetTimeout: int = 0) -> bool:

        command = bytearray([
            PN532_COMMAND_TGINITASTARGET,
            5,  # MODE: PICC only, Passive only

            0x04, 0x00,  # SENS_RES
            0x00, 0x00, 0x00,  # NFCID1
            0x20,  # SEL_RES

            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,  # FeliCaParams
            0, 0,

            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # NFCID3t

            0,  # length of general bytes
            0  # length of historical bytes
        ])

        if (self.uid != b''):
            # if uid is set copy 3 bytes to nfcid1
            command[4] = self.uid[0]
            command[5] = self.uid[1]
            command[6] = self.uid[2]

        if (1 != self.pn532.tgInitAsTarget(command, tgInitAsTargetTimeout)):
            DMSG("tgInitAsTarget failed or timed out!")
            return False

        compatibility_container = bytearray([
            0, 0x0F,
            0x20,
            0, 0x54,
            0, 0xFF,
            0x04,  # T
            0x06,  # L
            0xE1, 0x04,  # File identifier
            ((NDEF_MAX_LENGTH & 0xFF00) >> 8), (NDEF_MAX_LENGTH & 0xFF),  # maximum NDEF file size
            0x00,  # read access 0x0 = granted
            0x00  # write access 0x0 = granted | 0xFF = deny
        ])

        if (self.tagWriteable == False):
            compatibility_container[14] = 0xFF

        self.tagWrittenByInitiator = False

        self.currentFile = TAGFILE_NONE
        runLoop = True

        while (runLoop):
            status, rx_data = self.pn532.tgGetData()
            if (status < 0):
                DMSG("tgGetData failed!\n")
                self.pn532.inRelease()
                return True

            # TODO: Pretty sure we can leverage these better
            p1 = rx_data[C_APDU_P1]
            p2 = rx_data[C_APDU_P2]
            lc = rx_data[C_APDU_LC]
            p1p2_length = (p1 << 8) + p2
            out_buf = bytearray()

            if rx_data[C_APDU_INS] == ISO7816_SELECT_FILE:
                if p1 == C_APDU_P1_SELECT_BY_ID:
                    if (p2 != 0x0c):
                        DMSG("C_APDU_P2 != 0x0c\n")
                        out_buf = self.setResponse(RESPCMD_COMMAND_COMPLETE)
                    elif (lc == 2 and rx_data[C_APDU_DATA] == 0xE1 and (
                            rx_data[C_APDU_DATA + 1] == 0x03 or rx_data[C_APDU_DATA + 1] == 0x04)):
                        out_buf = self.setResponse(RESPCMD_COMMAND_COMPLETE)
                        if (rx_data[C_APDU_DATA + 1] == 0x03):
                            self.currentFile = TAGFILE_CC
                        elif (rx_data[C_APDU_DATA + 1] == 0x04):
                            self.currentFile = TAGFILE_NDEF
                    else:
                        out_buf = self.setResponse(RESPCMD_TAG_NOT_FOUND)
                elif p1 == C_APDU_P1_SELECT_BY_NAME:
                    ndef_tag_application_name_v2 = bytearray([0, 0x7, 0xD2, 0x76, 0x00, 0x00, 0x85, 0x01, 0x01])
                    if (ndef_tag_application_name_v2 == rx_data[
                                                        C_APDU_P2: C_APDU_P2 + len(ndef_tag_application_name_v2)]):
                        self.currentFile = TAGFILE_NDEF     # Pretty sure we need this here?
                        out_buf = self.setResponse(RESPCMD_COMMAND_COMPLETE)
                    else:
                        DMSG("function not supported\n")
                        out_buf = self.setResponse(RESPCMD_FUNCTION_NOT_SUPPORTED)
            elif rx_data[C_APDU_INS] == ISO7816_READ_BINARY:
                if self.currentFile == TAGFILE_NONE:
                    out_buf = self.setResponse(RESPCMD_TAG_NOT_FOUND)
                elif self.currentFile == TAGFILE_CC:
                    if (p1p2_length > NDEF_MAX_LENGTH):
                        out_buf = self.setResponse(RESPCMD_END_OF_FILE_BEFORE_REACHED_LE_BYTES)
                    else:
                        out_buf = compatibility_container[p1p2_length: p1p2_length + lc]
                        out_buf += self.setResponse(RESPCMD_COMMAND_COMPLETE)
                elif self.currentFile == TAGFILE_NDEF:
                    if (p1p2_length > NDEF_MAX_LENGTH):
                        out_buf = self.setResponse(RESPCMD_END_OF_FILE_BEFORE_REACHED_LE_BYTES)
                    else:
                        out_buf = self.ndef_file[p1p2_length: p1p2_length + lc]
                        out_buf += self.setResponse(RESPCMD_COMMAND_COMPLETE)
            elif rx_data[C_APDU_INS] == ISO7816_UPDATE_BINARY:
                if (not self.tagWriteable):
                    out_buf = self.setResponse(RESPCMD_FUNCTION_NOT_SUPPORTED)
                else:
                    if (p1p2_length > NDEF_MAX_LENGTH):
                        out_buf = self.setResponse(RESPCMD_MEMORY_FAILURE)
                    else:
                        self.ndef_file = self.ndef_file[:p1p2_length] + rx_data[C_APDU_DATA: C_APDU_DATA + lc] + self.ndef_file[p1p2_length + lc:]
                        out_buf = self.setResponse(RESPCMD_COMMAND_COMPLETE)
                        self.tagWrittenByInitiator = True

                        ndef_length = (self.ndef_file[0] << 8) + self.ndef_file[1]
                        if ((ndef_length > 0) and (self.updateNdefCallback != None)):
                            self.updateNdefCallback(self.ndef_file[2:])
            else:
                DMSG("Command not supported! {:x}".format(rx_data[C_APDU_INS]))
                out_buf = self.setResponse(RESPCMD_FUNCTION_NOT_SUPPORTED)
            status = self.pn532.tgSetData(out_buf)
            if not status:
                DMSG("tgSetData failed\n!")
                self.pn532.inRelease()
                return True
        self.pn532.inRelease()
        return True

    def setResponse(self, cmd: int) -> (bytearray):
        buf = bytearray()
        if cmd == RESPCMD_COMMAND_COMPLETE:
            buf = bytearray([R_APDU_SW1_COMMAND_COMPLETE, R_APDU_SW2_COMMAND_COMPLETE])
        elif cmd == RESPCMD_TAG_NOT_FOUND:
            buf = bytearray([R_APDU_SW1_NDEF_TAG_NOT_FOUND, R_APDU_SW2_NDEF_TAG_NOT_FOUND])
        elif cmd == RESPCMD_FUNCTION_NOT_SUPPORTED:
            buf = bytearray([R_APDU_SW1_FUNCTION_NOT_SUPPORTED, R_APDU_SW2_FUNCTION_NOT_SUPPORTED])
        elif cmd == RESPCMD_MEMORY_FAILURE:
            buf = bytearray([R_APDU_SW1_MEMORY_FAILURE, R_APDU_SW2_MEMORY_FAILURE])
        elif cmd == RESPCMD_END_OF_FILE_BEFORE_REACHED_LE_BYTES:
            buf = bytearray([R_APDU_SW1_END_OF_FILE_BEFORE_REACHED_LE_BYTES,
                             R_APDU_SW2_END_OF_FILE_BEFORE_REACHED_LE_BYTES])
        return buf
