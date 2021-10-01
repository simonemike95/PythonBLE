#!/usr/bin/python3
import sys, subprocess, re, os, logging
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from datetime import datetime

from Advertisement import Advertisement, InvalidArgsException
from Advertisement import register_ad_cb
from Advertisement import LE_ADVERTISEMENT_IFACE, LE_ADVERTISING_MANAGER_IFACE
from GattServer import Service, Characteristic
from GattServer import register_app_cb
from GattServer import BLUEZ_SERVICE_NAME, GATT_MANAGER_IFACE, DBUS_OM_IFACE, DBUS_PROP_IFACE
from GattServer import GATT_SERVICE_IFACE, GATT_CHRC_IFACE, GATT_DESC_IFACE

# STEP 1
# If you want to add a new service or characteristic, it should be added similar to the following
# each service and characteristic will be its own class, with its own UUIDs and name
from RxTx import RxTxService, RxTxCharacteristic, RXTX_SERVICE_UUID, RXTX_SERVICE_NAME

LOCAL_NAME =    "gatt-server"
mainloop = None

today = datetime.now()
dt_string = today.strftime("%d-%m-%Y_%H:%M:%S")

if os.path.exists(f"/data/") == False:
    os.mkdir("/data")

if os.path.exists(f"/data/logs/") == False:
    os.mkdir("/data/logs")

with open(f"/data/logs/{dt_string}.txt", 'w') as f: # Create the log file
    pass

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(f"/data/logs/{dt_string}.txt")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = "/"
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        logging.info(f"Adding service {str(service)}")
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response

class UartApplication(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        # STEP 2
        # The services should be added here
        self.add_service(RxTxService(bus, 0))

class UartAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        # STEP 3
        # UUIDs for the service need to be added here
        self.add_service_uuid(RXTX_SERVICE_UUID)
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True

def register_app_error_cb(error):
    logging.debug("Failed to register application.")
    logging.debug(f"Error:\n{str(error)}")
    mainloop.quit()

def register_ad_error_cb(error):
    logging.debug("Failed to register advertisement.")
    logging.debug(f"Error:\n{str(error)}")
    mainloop.quit()

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()
    for o, props in objects.items():
        if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
            logging.info(f"Returning adapter: {o}")
            return o
        logging.info(f"Skipping adapter: {o}")
    return None

def set_profile():
    fh = open("/home/root/sdp_record.xml", "r")
    sdp = fh.read()
    fh.close()
    opts = {
        "AutoConnect": True,
        "ServiceRecord": sdp
    }
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")
    
    # OPTIONAL STEP 4
    # You can change the UUID for the profile advertised here
    manager.RegisterProfile("/org/bluez/hci0", "00001124-0000-1000-8000-00805f9b34fb", opts)

def main():
    global mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)

    if not adapter:
        logging.debug("BLE adapter not found")
        return
 
    service_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)

    app = UartApplication(bus)
    adv = UartAdvertisement(bus, 0)
    mainloop = GLib.MainLoop()

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)
    ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)
    try:
        mainloop.run()
    except KeyboardInterrupt:
        adv.Release()

if __name__ == "__main__":
    main()
