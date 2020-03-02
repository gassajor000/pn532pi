# snep_test.ino
# send a SNEP message to android and get a message from android
import binascii
import time

from PN532.pn532 import pn532
from PN532.snep import snep
from PN532_SPI.pn532spi import pn532spi

PN532_SPI = pn532spi(pn532spi.SS0_GPIO8)
nfc = snep(pn532(PN532_SPI))


def setup():
    print("-------Peer to Peer--------")
    PN532_SPI.begin()


message = bytearray([
    0xD2, 0xA, 0xB, 0x74, 0x65, 0x78, 0x74, 0x2F, 0x70, 0x6C,
    0x61, 0x69, 0x6E, 0x68, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77,
    0x6F, 0x72, 0x6C, 0x64])


def loop():
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
