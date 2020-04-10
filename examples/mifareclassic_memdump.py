"""
    This example attempts to dump the contents of a Mifare Classic 1K card

    Note that you need the baud rate to be 115200 because we need to print
    out the data and read from the card at the same time!

    To enable debug message, define DEBUG in nfc/pn532_debug.h
"""
import binascii

from pn532pi import pn532, Pn532
from pn532pi import Pn532Hsu
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi

SPI = False
I2C = False
HSU = True

if SPI:
    PN532_SPI = Pn532Spi(Pn532Spi.SS0_GPIO8)
    nfc = Pn532(PN532_SPI)
# When the number after #elif set as 1, it will be switch to HSU Mode
elif HSU:
    PN532_HSU = Pn532Hsu(Pn532Hsu.RPI_MINI_UART)
    nfc = Pn532(PN532_HSU)

# When the number after #if & #elif set as 0, it will be switch to I2C Mode
elif I2C:
    PN532_I2C = Pn532I2c(1)
    nfc = Pn532(PN532_I2C)


def setup():
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
  authenticated = False               # Flag to indicate if the sector is authenticated

  # Keyb on NDEF and Mifare Classic should be the same
  keyuniversal = bytearray([ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ])

  # Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
  # 'uid' will be populated with the UID, and uidLength will indicate
  # if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
  success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

  if (success):
    # Display some basic information about the card
    print("Found an ISO14443A card")
    print("UID Length: {:d}".format(len(uid)))
    print("UID Value: {}".format(binascii.hexlify(uid)))

    if (len(uid) == 4):
      # We probably have a Mifare Classic card ...
      print("Seems to be a Mifare Classic card (4 byte UID)")

      # Now we try to go through all 16 sectors (each having 4 blocks)
      # authenticating each sector, and then dumping the blocks
      for currentblock in range(64):
        # Check if this is a new block so that we can reauthenticate
        if (nfc.mifareclassic_IsFirstBlock(currentblock)):
          authenticated = False

        # If the sector hasn't been authenticated, do so first
        if (not authenticated):
          # Starting of a new sector ... try to to authenticate
          print("------------------------Sector {:d}-------------------------".format(int(currentblock / 4)))
          if (currentblock == 0):
              # This will be 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF for Mifare Classic (non-NDEF!)
              # or 0xA0 0xA1 0xA2 0xA3 0xA4 0xA5 for NDEF formatted cards using key a,
              # but keyb should be the same for both (0xFF 0xFF 0xFF 0xFF 0xFF 0xFF)
              success = nfc.mifareclassic_AuthenticateBlock (uid, currentblock, 1, keyuniversal)
          else:
              # This will be 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF for Mifare Classic (non-NDEF!)
              # or 0xD3 0xF7 0xD3 0xF7 0xD3 0xF7 for NDEF formatted cards using key a,
              # but keyb should be the same for both (0xFF 0xFF 0xFF 0xFF 0xFF 0xFF)
              success = nfc.mifareclassic_AuthenticateBlock (uid, currentblock, 1, keyuniversal)
          if (success):
            authenticated = True
          else:
            print("Authentication error")
        # If we're still not authenticated just skip the block
        if (not authenticated):
          print("Block {:d}".format(currentblock))
          print(" unable to authenticate")
        else:
          # Authenticated ... we should be able to read the block now
          # Dump the data into the 'data' array
          success, data = nfc.mifareclassic_ReadDataBlock(currentblock)
          if (success):
            # Read successful
            print("Block {:d}".format(currentblock))
            if (currentblock < 10):
              print("  ")
            else:
              print(" ")
            # Dump the raw data
            print(binascii.hexlify(data))
          else:
            # Oops ... something happened
            print("Block {:d}".format(currentblock))
            print(" unable to read this block")
    else:
      print("Ooops ... this doesn't seem to be a Mifare Classic card!")

    # Wait a bit before trying again
    input("\n\nSend a character to run the mem dumper again!")


if __name__ == '__main__':
    setup()
    while True:
      loop()