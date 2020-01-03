"""
    This example will attempt to connect to an ISO14443A
    card or tag and retrieve some basic information about it
    that can be used to determine what type of card it is.   
   
    Note that you need the baud rate to be 115200 because we need to print
    out the data and read from the card at the same time! 

    To enable debug message, set DEBUG in PN532/PN532_debug.h
"""
import time

from PN532.pn532 import pn532, PN532_MIFARE_ISO14443A_106KBPS
from PN532_I2C.pn532i2c import pn532i2c
from PN532_SPI.pn532spi import pn532spi


# Set the desired interface to True
SPI = False
I2C = False
HSU = False

if SPI:
    PN532_SPI = pn532spi(pn532spi.SS0_GPIO8)
    nfc = pn532(PN532_SPI)
# When the number after #elif set as 1, it will be switch to HSU Mode
elif HSU:
    PN532_HSU = pn532hsu(Serial1)
    nfc = pn532(PN532_HSU)

# When the number after #if & #elif set as 0, it will be switch to I2C Mode
elif I2C:
    PN532_I2C = pn532i2c(1)
    nfc = pn532(PN532_I2C)


def setup():
    nfc.begin()

    versiondata = nfc.getFirmwareVersion()
    if not versiondata:
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    # Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))
    # Set the max number of retry attempts to read from a card
    # This prevents us from waiting forever for a card, which is
    # the default behaviour of the PN532.
    nfc.setPassiveActivationRetries(0xFF)

    # configure board to read RFID tags
    nfc.SAMConfig()

    print("Waiting for an ISO14443A card")


def loop():
    # Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
    # 'uid' will be populated with the UID, and uidLength will indicate
    # if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    success, uid = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A_106KBPS)

    if (success):
        print("Found a card!")
        print("UID Length: {:d}".format(len(uid)))
        print("UID Value: {}".format(uid))
        # Wait 1 second before continuing
        time.sleep(1)
        return True
    else:
        # PN532 probably timed out waiting for a card
        print("Timed out waiting for a card")
        return False


if __name__ == '__main__':
    setup()
    found = loop()
    while not found:
      found = loop()