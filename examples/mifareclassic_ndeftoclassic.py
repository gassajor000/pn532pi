"""
    This examples attempts to take a Mifare Classic 1K card that has been
    formatted for NDEF messages using mifareclassic_formatndef, and resets
    the authentication keys back to the Mifare Classic defaults

    To enable debug message, define DEBUG in nfc/pn532_debug.h
"""
import binascii
import time

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
    PN532_I2C = Pn532I2c(Pn532I2c.RPI_BUS1)
    nfc = Pn532(PN532_I2C)


NR_SHORTSECTOR          = 32    # Number of short sectors on Mifare 1K/4K
NR_LONGSECTOR           = 8     # Number of long sectors on Mifare 4K
NR_BLOCK_OF_SHORTSECTOR = 4     # Number of blocks in a short sector
NR_BLOCK_OF_LONGSECTOR  = 16    # Number of blocks in a long sector

# Determine the sector trailer block based on sector number
def BLOCK_NUMBER_OF_SECTOR_TRAILER(sector):
  return (sector)*NR_BLOCK_OF_SHORTSECTOR + NR_BLOCK_OF_SHORTSECTOR-1 if sector < NR_SHORTSECTOR else \
    NR_SHORTSECTOR*NR_BLOCK_OF_SHORTSECTOR + (sector-NR_SHORTSECTOR)*NR_BLOCK_OF_LONGSECTOR + NR_BLOCK_OF_LONGSECTOR-1

# Determine the sector's first block based on the sector number
def BLOCK_NUMBER_OF_SECTOR_1ST_BLOCK(sector):
  (sector) * NR_BLOCK_OF_SHORTSECTOR if sector < NR_SHORTSECTOR else \
    NR_SHORTSECTOR * NR_BLOCK_OF_SHORTSECTOR + (sector - NR_SHORTSECTOR) * NR_BLOCK_OF_LONGSECTOR


# The default Mifare Classic key
KEY_DEFAULT_KEYAB = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

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
  blankAccessBits = bytearray([0xff, 0x07, 0x80 ])
  numOfSector = 16                 # Assume Mifare Classic 1K for now (16 4-block sectors)
  
  print("Place your NDEF formatted Mifare Classic 1K card on the reader")
  # Wait for user input before proceeding
  input("and press any key to continue ...")
  
    
  # Wait for an ISO14443A type card (Mifare, etc.).  When one is found
  # 'uid' will be populated with the UID, and uidLength will indicate
  # if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
  success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

  if (success): 
    # We seem to have a tag ...
    # Display some basic information about it
    print("Found an ISO14443A card")
    print("UID Length: {:d}".format(len(uid)))
    print("UID Value: {}".format(binascii.hexlify(uid)))

    
    # Make sure this is a Mifare Classic card
    if (len(uid) != 4):
      print("Ooops ... this doesn't seem to be a Mifare Classic card!") 
      return
    
    print("Seems to be a Mifare Classic card (4 byte UID)")
    print("")
    print("Reformatting card for Mifare Classic (please don't touch it!) ... ")

    # Now run through the card sector by sector
    for idx in range(numOfSector):
      # Step 1: Authenticate the current sector using key B 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
      success = nfc.mifareclassic_AuthenticateBlock (uid, BLOCK_NUMBER_OF_SECTOR_TRAILER(idx), 1, KEY_DEFAULT_KEYAB)
      if (not success):
        print("Authentication failed for sector {}".format(numOfSector))
        return
      
      # Step 2: Write to the other blocks
      blockBuffer = bytearray(b'\x00'*16)
      if (idx == 16):
        if (not (nfc.mifareclassic_WriteDataBlock((BLOCK_NUMBER_OF_SECTOR_TRAILER(idx)) - 3, blockBuffer))):
          print("Unable to write to sector {}".format(numOfSector))
          return
      if ((idx == 0) or (idx == 16)):
        if (not (nfc.mifareclassic_WriteDataBlock((BLOCK_NUMBER_OF_SECTOR_TRAILER(idx)) - 2, blockBuffer))):
          print("Unable to write to sector {}".format(numOfSector))
          return
      else:
        if (not (nfc.mifareclassic_WriteDataBlock((BLOCK_NUMBER_OF_SECTOR_TRAILER(idx)) - 3, blockBuffer))):
          print("Unable to write to sector {}".format(numOfSector))
          return
        if (not (nfc.mifareclassic_WriteDataBlock((BLOCK_NUMBER_OF_SECTOR_TRAILER(idx)) - 2, blockBuffer))):
          print("Unable to write to sector {}".format(numOfSector))
          return

      blockBuffer = bytearray(b'\x00' * 16)
      if (not(nfc.mifareclassic_WriteDataBlock((BLOCK_NUMBER_OF_SECTOR_TRAILER(idx)) - 1, blockBuffer))):
        print("Unable to write to sector {}".format(numOfSector))
        return
      
      # Step 3: Reset both keys to 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
      blockBuffer = KEY_DEFAULT_KEYAB + blankAccessBits + b'\x69' + KEY_DEFAULT_KEYAB

      # Step 4: Write the trailer block
      if (not (nfc.mifareclassic_WriteDataBlock((BLOCK_NUMBER_OF_SECTOR_TRAILER(idx)), blockBuffer))):
        print("Unable to write trailer block of sector ")
        print(numOfSector)
        return
  
  # Wait a bit before trying again
  print("\n\nDone!")
  time.sleep(1)

if __name__ == '__main__':
    setup()
    while True:
      loop()