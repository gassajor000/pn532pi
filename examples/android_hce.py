import time
import binascii

from pn532pi import Pn532
from pn532pi import Pn532Hsu
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi

# Set the desired interface to True
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
  print("-------Peer to Peer HCE--------")

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
  #nfc.setPassiveActivationRetries(0xFF)

  # configure board to read RFID tags
  nfc.SAMConfig()

def loop():
  print("Waiting for an ISO14443A card")

  # set shield to inListPassiveTarget
  success = nfc.inListPassiveTarget()

  if (success):

    print("Found something!")

    selectApdu = bytearray([0x00,                                     # CLA 
                            0xA4,                                     # INS 
                            0x04,                                     # P1  
                            0x00,                                     # P2  
                            0x07,                                     # Length of AID  
                            0xF0, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, # AID defined on Android App 
                            0x00 # Le
                            ])

    success, response = nfc.inDataExchange(selectApdu)

    if (success):

      print("responseLength: {:d}", len(response))
      print(binascii.hexlify(response))

      while (success):
        apdu = bytearray(b"Hello from Arduino")
        success, back = nfc.inDataExchange(apdu)

        if (success):
          print("responseLength: {:d}", len(back))
          print(binascii.hexlify(back))
        else:
          print("Broken connection?")
    else:
      print("Failed sending SELECT AID")
  else:
    print("Didn't find anything!")

  time.sleep(1)


def setupNFC():
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

if __name__ == '__main__':
    setup()
    while True:
      loop()