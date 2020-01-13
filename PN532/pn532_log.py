"""
    created by Jordan Gassaway, 1/12/2020
    pn532_log: Logging functions for pn532 classes
"""

DEBUG = False


def DMSG(msg):
    if DEBUG:
        print(msg)


def DMSG_HEX(char):
    if DEBUG:
        print('%x' % char)


def PrintHex(data: bytearray):
    """
        Prints a hexadecimal value in plain characters

        :param data:      data to print
    """
    print("".join('{:2X}'.format(x) for x in data))


def PrintHexChar(data: bytearray, numBytes: int):
    """
    Prints a hexadecimal value in plain characters, along with
        the char equivalents in the following format

        00 00 00 00 00 00  ......

    :param data: data to print
    """
    for i in range(numBytes):
        print(" {:2X}".format(data[i]))

    print("    ")
    for i in range(numBytes):
        c = data[i]
        if (c <= 0x1f or c > 0x7f):
            print(".")
        else:
            print("%c" % c)

        print("\n")