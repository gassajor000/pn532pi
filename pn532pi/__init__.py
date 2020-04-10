try:
    from pn532pi.interfaces.pn532i2c import Pn532I2c
    from pn532pi.interfaces.pn532spi import Pn532Spi
    from pn532pi.interfaces.pn532hsu import Pn532Hsu
except:        # Allow unit tests to run without importing interfaces
    Pn532Hsu = None
    Pn532Spi = None
    Pn532I2c = None


from pn532pi.nfc.pn532_log import DEBUG
from pn532pi.nfc import pn532
from pn532pi.nfc.pn532 import Pn532
from pn532pi.nfc.llcp import Llcp
from pn532pi.nfc.snep import Snep
from pn532pi.nfc.emulatetag import EmulateTag
