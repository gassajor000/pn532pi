## NFC library for Raspberry Pi

This is a port of [Seeed Studios's PN532 Arduino Library](https://github.com/Seeed-Studio/PN532) for using the PN532 chip with Raspberry Pi. 

![Raspberry Pi](https://github.com/gassajor000/pyndef/blob/master/14643-Raspberry_Pi_3_B_-02.jpg?raw=true)
![PN532](https://github.com/gassajor000/pyndef/blob/master/PN532--NFC-RFID-Module.jpg?raw=true)

### Features
+ Support all interfaces of PN532 (I2C, SPI, HSU )
+ Read/write Mifare Classic Card
+ Communicate with android 4.0+([Lists of devices supported](https://github.com/Seeed-Studio/PN532/wiki/List-of-devices-supported))
+ Card emulation (NFC Type 4 tag)

### To Do
+ Works with [Don's NDEF Library](http://goo.gl/jDjsXl)
+ To support more than one INFO PDU of P2P communication
+ To read/write NFC Type 4 tag

### Getting Started
+ Easy way

  1. Download [zip file](https://github.com/gassajor000/pyndef/archive/master.zip) and extract the 4 folders(PN532, PN532_SPI, PN532_I2C and PN532_HSU) into Arduino's libraries.
  2. TODO: Download [Don's NDEF library](http://goo.gl/ewxeAe)， extract it into Arduino's libraries and rename it to NDEF.
  3. Follow the examples of the two libraries.

+ Git way for Linux/Mac (recommended)

  1. Get PN532 library and NDEF library

          cd {Arduino}\libraries  
          git clone --recursive https://github.com/gassajor000/pyndef.git NFC
          ln -s NFC/PN532 ./
          ln -s NFC/PN532_SPI ./
          ln -s NFC/PN532_I2C ./
          ln -s NFC/PN532_HSU ./
          ln -s NFC/NDEF ./

  2. Follow the examples of the two libraries

## Power
The Raspberry Pi does not provide enough current to drive the PN532 chip. 
If you try to run the PN532 off your Raspberry Pi it will reset randomly and may not respond to commands.
Instead you will need another power source (3.3v) to power the PN532

## I2C Interface

I2C is short for Inter-integrated Circuit. I2C interface needs only 4 wires to connect PN532 with Raspbeery Pi.
![I2C Connection](https://github.com/gassajor000/pyndef/blob/master/rpi_i2c_connection.png?raw=true)

To use the I2C bus 1 to control PN532, refer to the code below.
```python
from PN532_I2C.pn532i2c import pn532i2c
from PN532.pn532 import pn532
	
i2c = pn532i2c(1)
nfc = pn532(i2c)

def setup():
    nfc.begin()
    # ...
```

### Contribution
It's based on [Adafruit_NFCShield_I2C](http://goo.gl/pk3FdB). 
[Seeed Studio](http://goo.gl/zh1iQh) rewrite the library to make it easy to support different interfaces and platforms. 
@Don writes the [NDEF library](http://goo.gl/jDjsXl) to make it more easy to use. 
@JiapengLi adds HSU interface.
@awieser adds card emulation function.
@gassajor000 ported to python/Raspberry Pi

[Mega]: http://arduino.cc/en/Main/ arduinoBoardMega
[DUE]: http://arduino.cc/en/Main/arduinoBoardDue
[Leonardo]: http://arduino.cc/en/Main/arduinoBoardLeonardo
[SoftwareSerial]: https://www.arduino.cc/en/Reference/softwareSerial

Images courtesy of 
[pinout.xyz](https://pinout.xyz/), [components101.com](https://components101.com/wireless/pn532-nfc-rfid-module), [sparkfun.com](https://www.sparkfun.com/products/14643)  

