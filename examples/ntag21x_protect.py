# NTAG21x supports 4 bytes password to protect pages started from AUTH0
# AUTH0 defines the page address from which the password verification is required.
# Valid address range for byte AUTH0 is from 00h to FFh.
# If AUTH0 is set to a page address which is higher than the last page from the user configuration,
# the password protection is effectively disabled
import time
import binascii

from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi
from pn532pi import Pn532Hsu

# Set the desired interface to True
SPI = False
I2C = False
HSU = True


if SPI:
    PN532_SPI = Pn532Spi(Pn532Spi.SS0_GPIO8)
    nfc = Pn532(PN532_SPI)
elif HSU:
    PN532_HSU = Pn532Hsu(0)
    nfc = Pn532(PN532_HSU)

elif I2C:
    PN532_I2C = Pn532I2c(1)
    nfc = Pn532(PN532_I2C)


password = bytearray([0x12, 0x34, 0x56, 0x78])


def setup():
    print("NTAG21x Protect")
    print("-------Looking for PN532--------")

    nfc.begin()

    versiondata = nfc.getFirmwareVersion()
    if not versiondata:
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    # Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))

    # configure board to read RFID tags
    nfc.SAMConfig()

def loop():
    print("wait for a tag")
    # wait until a tag is present
    tag_present, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

    if (tag_present):
        # Display some basic information about the card
        print("Found a card!")
        print("UID Length: {:d}".format(len(uid)))
        print("UID Value: {}".format(binascii.hexlify(uid)))

    # if NTAG21x enables r/w protection, uncomment the following line
    # nfc.ntag21x_auth(password)

    status, buf = nfc.mifareultralight_ReadPage(3)
    capacity = int(buf[2])
    print("Tag capacity {:d} bytes".format(capacity*8))

    cfg_page_base = 0x29   # NTAG213
    if (capacity == 0x3E):
        cfg_page_base = 0x83       # NTAG215
    elif (capacity == 0x6D):
        cfg_page_base = 0xE3       # NTAG216

    # PWD page, set new password
    nfc.mifareultralight_WritePage(cfg_page_base + 2, password)

    # disable r/w
    # | PROT | CFG_LCK | RFUI | NFC_CNT_EN | NFC_CNT_PWD_PROT | AUTHLIM (2:0) |
    buf[0] = (1 << 7) | 0x0
    nfc.mifareultralight_WritePage(cfg_page_base + 1, buf)

    # protect pages started from AUTH0
    auth0 = 0x10
    buf[0] = 0
    buf[1] = 0
    buf[2] = 0
    buf[3] = auth0
    nfc.mifareultralight_WritePage(cfg_page_base, buf)

    # wait until the tag is removed
    while tag_present:
        time.sleep(.1)
        tag_present, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)


if __name__ == '__main__':
    setup()
    while True:
        loop()
