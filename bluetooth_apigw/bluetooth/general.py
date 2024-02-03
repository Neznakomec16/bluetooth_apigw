#!/usr/bin/python3
import dbus

from . import constants

adapter_interface = None
mainloop = None


def get_adapters():
    # get all objects in the bluez service
    manager_obj = manager.GetManagedObjects()
    # iterate through them
    for path, ifaces in manager_obj.items():
        # if the org.bluez.Adapter1 interface is supported by this object, store its address and path
        if constants.ADAPTER_INTERFACE in ifaces:
            adapter_paths.append(path)
            adapter_addresses.append(manager_obj[path][constants.ADAPTER_INTERFACE]["Address"])

    return (adapter_paths, adapter_addresses)


def getDeviceProxy(bus, bdaddr):
    manager = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, "/"), constants.DBUS_OM_IFACE
    )
    objects = manager.GetManagedObjects()
    for path, ifaces in objects.items():
        device = ifaces.get(constants.DEVICE_INTERFACE)
        if device is None:
            continue
        else:
            if device["Address"] == bdaddr:
                device_object = bus.get_object(constants.BLUEZ_SERVICE_NAME, path)
                return dbus.Interface(device_object, constants.DEVICE_INTERFACE)


def is_connected(bus, device_path):
    props = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, device_path),
        constants.DBUS_PROPERTIES,
    )
    connected = props.Get(constants.DEVICE_INTERFACE, "Connected")
    return connected
