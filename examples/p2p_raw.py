# snep_test.ino
# send a SNEP message to android and get a message from android
import time
import binascii

from pn532pi import Pn532
from pn532pi import Snep
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi
from pn532pi import Pn532Hsu


# Set the desired interface to True
SPI = False
I2C = False
HSU = True

if SPI:
    PN532_SPI = Pn532Spi(Pn532Spi.SS0_GPIO8)
    PN532 = Pn532(PN532_SPI)
# When the number after #elif set as 1, it will be switch to HSU Mode
elif HSU:
    PN532_HSU = Pn532Hsu(0)
    PN532 = Pn532(PN532_HSU)

# When the number after #if & #elif set as 0, it will be switch to I2C Mode
elif I2C:
    PN532_I2C = Pn532I2c(1)
    PN532 = Pn532(PN532_I2C)

nfc = Snep(PN532)


def setup():
    print("-------Peer to Peer--------")
    PN532.begin()

    versiondata = PN532.getFirmwareVersion()
    if not versiondata:
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    # Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))


message = bytearray([
    0xD2, 0xA, 0xB, 0x74, 0x65, 0x78, 0x74, 0x2F, 0x70, 0x6C,
    0x61, 0x69, 0x6E, 0x68, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77,
    0x6F, 0x72, 0x6C, 0x64])


def loop():
    print("Sending SNEP message")    
    nfc.write(message)
    time.sleep(3)

    status, buf = nfc.read()
    if status > 0:
        print("get a SNEP message:")
        print(binascii.hexlify(buf))
        print(buf)
        print('\n')

    time.sleep(3)


if __name__ == '__main__':
    setup()
    while True:
        loop()
