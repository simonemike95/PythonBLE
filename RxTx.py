#!/usr/bin/python3
import sys, logging
import dbus, dbus.mainloop.glib
from gi.repository import GLib

from Advertisement import Advertisement
from Advertisement import register_ad_cb
from GattServer import Service, Characteristic
from GattServer import register_app_cb
from GattServer import GATT_CHRC_IFACE

# You can basically make these anything you want
RXTX_SERVICE_NAME =             "org.bluez.GattServices.RxTx"
RXTX_SERVICE_UUID =             "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
RXTX_CHARACTERISTIC_NAME =      "org.bluez.GattCharacteristics.RxTx"
RXTX_CHARACTERISTIC_UUID =      "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
RXTX_DESC =                     "org.bluez.GattDescriptors.RxTx"

class RxTxService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, RXTX_SERVICE_UUID, True)
        self.add_characteristic(RxTxCharacteristic(bus, 0, self))

class RxTxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index,
                                RXTX_CHARACTERISTIC_UUID,
                                ["write", "notify", "write-without-response"],
                                service)
        self.notifying = True
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.ReceiveCommand)

    def ReceiveCommand(self, value, options):
        try:
            data = bytearray(value)
        except Exception as e:
            logging.info(f"Error: {e}")

        data = data.decode()
        logging.info(f"Received command: {data[0:-1]}")
        self.ProcessCommand(data)

    def ProcessCommand(self, cmd):
        # Custom commands can be read by checking for string values

        # I usually just create functions that correspond to the commands and
        # execute the functions when the command is received

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

    def SendResponse(self, s):
        s = s + "\\n"

        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        logging.info(f"Sending TX {s}")

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
 
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False


## Command functions ##
    def testCmd(self):
        self.SendResponse("Received test cmd")