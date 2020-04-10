## NFC library for Raspberry Pi

This is a port of [Seeed Studios's PN532 Arduino Library](https://github.com/Seeed-Studio/PN532) for using the PN532 chip with Raspberry Pi. 

![Raspberry Pi](https://github.com/gassajor000/pn532pi/blob/master/docs/14643-Raspberry_Pi_3_B_-02.jpg?raw=true)
![PN532](https://github.com/gassajor000/pn532pi/blob/master/docs/PN532--NFC-RFID-Module.jpg?raw=true)

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
+ PyPI
    1. Install with pip
        ```
        pip install pn532pi
        ```
    2. Follow examples
+ Direct Download

    1. Download [zip file](https://github.com/gassajor000/pn532pi/archive/master.zip) and extract the 4 folders(pn532pi, quick2wire, examples and test)
    2. Follow the examples of the two libraries.

+ Clone Git Repository

    1. Get pn532 library
        ```
          git clone --recursive https://github.com/gassajor000/pn532pi.git
        ```
    
    2. Follow the examples of the two libraries

## Power
The Raspberry Pi does not provide enough current to drive the PN532 chip. 
If you try to run the PN532 off your Raspberry Pi it will reset randomly and may not respond to commands.
Instead you will need another power source (3.3v) to power the PN532

## I2C Interface

I2C is short for Inter-integrated Circuit. I2C interface needs only 4 wires to connect PN532 with Raspbeery Pi.
![I2C Connection](https://github.com/gassajor000/pn532pi/blob/master/docs/rpi_i2c_connection.png?raw=true)

To use the I2C bus 1 to control PN532, refer to the code below.
```python
from pn532pi import Pn532I2c, Pn532
	
i2c = Pn532I2c(1)
nfc = Pn532(i2c)

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

