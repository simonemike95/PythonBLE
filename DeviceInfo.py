#!/usr/bin/python3
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from gi.repository import GObject

from Advertisement import Advertisement
from Advertisement import register_ad_cb
from GattServer import Service, Characteristic
from GattServer import register_app_cb
from GattServer import GATT_CHRC_IFACE

# You can basically make these anything you want
DEVICE_INFO_SERVICE_NAME =        "org.bluez.GattServices.DeviceInfo"
DEVICE_INFO_SERVICE_UUID =        "0000180a-0000-1000-8000-00805f9b34fb"
DEVICE_INFO_CHARACTERISTIC_NAME =  "org.bluez.GattCharacteristics.DeviceInfo"
DEVICE_INFO_CHARACTERISTIC_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
DEVICE_INFO_DESC =                "org.bluez.GattDescriptors.DeviceInfo"