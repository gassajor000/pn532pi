"""
    This example will attempt to connect to an FeliCa
    card or tag and retrieve some basic information about it
    that can be used to determine what type of card it is.

    To enable debug message, define DEBUG in pn532/pn532_debug.h
"""
import time
import binascii

from pn532pi import Pn532
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

_prevIDm = bytearray(b'\x00' * 8)
_prevTime = 0


def millis():
    return int(round(time.time() * 1000))


def setup():
    print("NTAG21x R/W")
    print("-------Looking for pn532--------")

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
    # the default behaviour of the pn532.
    nfc.setPassiveActivationRetries(0xFF)
    nfc.SAMConfig()


def loop():
    global _prevIDm, _prevTime
    systemCode = 0xFFFF
    requestCode = 0x01  # System Code request

    # Wait for an FeliCa type cards.
    # When one is found, some basic information such as IDm, PMm, and System Code are retrieved.
    print("Waiting for an FeliCa card...  ")
    ret, idm, pwm, systemCodeResponse = nfc.felica_Polling(systemCode, requestCode, 5000)

    if (ret != 1):
        print("Could not find a card")
        time.sleep(.5)
        return

    if (idm == _prevIDm):
        if ((millis() - _prevTime) < 3000):
            print("Same card")
            time.sleep(.5)
            return

    print("Found a card!")
    print("  IDm : {}".format(binascii.hexlify(idm)))
    print("  PWm: {}".format(binascii.hexlify(pwm)))
    print("  System Code: {:x}".format(binascii.hexlify(systemCode)))

    _prevIDm = idm
    _prevTime = millis()

    print("Write Without Encryption command ")
    serviceCodeList = [0x0009]
    blockList = [0x8000]
    now = millis() & 0xFFFFFFFF  # unsigned long
    blockData = [bytearray(now.to_bytes(4, byteorder='big'))]
    print("   Writing current millis ({}) to Block 0 -> ".format(blockData))
    ret = nfc.felica_WriteWithoutEncryption(serviceCodeList, blockList, blockData)
    if (ret != 1):
        print("error")
    else:
        print("OK!")

    print("Read Without Encryption command -> ")
    serviceCodeList[0] = 0x000B
    blockList = [0x8000, 0x8001, 0x8002]
    ret, blockData = nfc.felica_ReadWithoutEncryption(serviceCodeList, blockList)
    if (ret != 1):
        print("error")
    else:
        print("OK!")
        for i in range(3):
            print("  Block no. {}: {}".format(i, binascii.hexlify(blockData[i])))

    # Wait 1 second before continuing
    print("Card access completed!\n")
    time.sleep(1)


if __name__ == '__main__':
    setup()
    while True:
        loop()
