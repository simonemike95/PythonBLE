#!/usr/bin/python3
import sys, logging
import dbus, dbus.mainloop.glib
from gi.repository import GLib

from Advertisement import Advertisement
from Advertisement import register_ad_cb
from GattServer import Service, Characteristic
from GattServer import register_app_cb
from GattServer import GATT_CHRC_IFACE


# There are specific reserved UUIDs for things like heart rate monitoring, battery level, etc.
# But for the most part, you can basically make these anything you want.
# Be sure to add any new services and/or characteristics to the advertising
RXTX_SERVICE_NAME =             "org.bluez.GattServices.RxTx"
RXTX_SERVICE_UUID =             "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
RXTX_CHARACTERISTIC_NAME =      "org.bluez.GattCharacteristics.RxTx"
RXTX_CHARACTERISTIC_UUID =      "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
RXTX_DESC =                     "org.bluez.GattDescriptors.RxTx"

# Necessary class - naming can be whatever you want
class RxTxService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, RXTX_SERVICE_UUID, True)
        self.add_characteristic(RxTxCharacteristic(bus, 0, self))

# Necesary class - naming can be whatever you want
class RxTxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index,
                                RXTX_CHARACTERISTIC_UUID,
                                ["write", "notify", "write-without-response"],
                                service)
        self.notifying = True
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.ReceiveCommand)

    # Necessary function - just make sure the name matches on line 36
    # You can customize this a bit to receive commands differently if you'd rather parse
    # simple hex numbers, check bits in a byte, etc.
    def ReceiveCommand(self, value, options):
        try:
            data = bytearray(value)
        except Exception as e:
            logging.info(f"Error: {e}")

        data = data.decode()
        
        # Logging is set up in main.py and is entirely optional
        logging.info(f"Received command: {data[0:-1]}")
        self.ProcessCommand(data)

    # Optional function - this processing can be done in the ReceiveCommand function
    # I typically break it out into its own function for readability
    def ProcessCommand(self, cmd):
        # Custom commands can be read by checking for string values, hex numbers, bits, etc.

        # I usually just create functions that correspond to the commands and
        # execute the functions when the command is received. This helps to keep
        # the code a bit more readable and maintainable.
        
        # To add a new command, you'll want to add a check for the string, number, etc.
        # Then either perform the functions you want based on the command in this function,
        # or create a new function and call it from here.

        if "test" in cmd:
            self.testCmd()
        elif "" in cmd:
            # Run your command function here
            pass
        else:
            # must be an invalid command
            logging.debug("Invalid command received")
            self.SendResponse("Invalid command")

        return True

    # Necessary function - if you want to ack your commands somehow, you'll need to
    # utilize this function, or one similar to it, and call it where you receive/process commands.
    def SendResponse(self, s):
        s = s + "\\n"

        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        logging.info(f"Sending TX {s}")

    # Necessary function - nothing needs to be added/changed here
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
 
    # Necessary function - nothing needs to be added/changed here
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False


    ## Command functions ##
    
    # Optional function(s) based on how you want to structure your code.
    
    def testCmd(self):
        self.SendResponse("Received test cmd")
