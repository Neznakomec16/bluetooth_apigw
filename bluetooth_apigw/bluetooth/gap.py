#!/usr/bin/python3
import dbus
import dbus.mainloop.glib

from . import constants, general, utils

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

adapter_interface = None
mainloop = None
timer_id = None
devices = {}


def interfaces_added(path, interfaces):
    if constants.DEVICE_INTERFACE not in interfaces:
        return
    properties = interfaces[constants.DEVICE_INTERFACE]
    if path in devices:
        dev = devices[path]
        devices[path] = devices[path] | properties
    else:
        devices[path] = properties
    if "Address" in devices[path]:
        address = properties["Address"]
    else:
        address = "<unknown>"


def properties_changed(interface, changed, invalidated, path):
    if interface != constants.DEVICE_INTERFACE:
        return
    if path in devices:
        dev = devices[path]
        devices[path] = dict(devices[path].items())
        devices[path].update(changed.items())
    else:
        devices[path] = changed

    if "Address" in devices[path]:
        address = devices[path]["Address"]
    else:
        address = "<unknown>"


def discovery_timeout():
    global adapter_interface
    global mainloop
    global timer_id
    GObject.source_remove(timer_id)
    mainloop.quit()
    adapter_interface.StopDiscovery()
    bus = dbus.SystemBus()
    bus.remove_signal_receiver(interfaces_added, "InterfacesAdded")
    bus.remove_signal_receiver(properties_changed, "PropertiesChanged")
    return True


def discover_devices(timeout):
    global adapter_interface
    global mainloop
    global timer_id
    adapter_paths = []
    adapter_addresses = []
    selected_adapter_path = ""
    selected_adapter_addr = ""

    selected_adapter_path = constants.BLUEZ_NAMESPACE + constants.ADAPTER_NAME

    # dbus initialisation steps
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    manager = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, "/"), constants.DBUS_OM_IFACE
    )

    # acquire the adapter interface so we can call its methods
    adapter_object = bus.get_object(constants.BLUEZ_SERVICE_NAME, selected_adapter_path)
    adapter_interface = dbus.Interface(adapter_object, constants.ADAPTER_INTERFACE)

    # register signal handler functions so we can asynchronously report discovered devices
    bus.add_signal_receiver(
        interfaces_added,
        dbus_interface=constants.DBUS_OM_IFACE,
        signal_name="InterfacesAdded",
    )

    bus.add_signal_receiver(
        properties_changed,
        dbus_interface=constants.DBUS_PROPERTIES,
        signal_name="PropertiesChanged",
        arg0=constants.DEVICE_INTERFACE,
        path_keyword="path",
    )

    objects = manager.GetManagedObjects()
    for path, interfaces in objects.items():
        if constants.DEVICE_INTERFACE in interfaces:
            interfaces_added(path, interfaces)

    mainloop = GObject.MainLoop()
    timer_id = GObject.timeout_add(timeout, discovery_timeout)
    adapter_interface.StartDiscovery(byte_arrays=True)

    mainloop.run()
    device_list = devices.values()
    discovered_devices = []
    for device in device_list:
        dev = {}
        if "Address" in device:
            dev["bdaddr"] = utils.dbus_to_python(device["Address"])
        if "Name" in device:
            dev["name"] = utils.dbus_to_python(device["Name"])
        if "ServicesResolved" in device:
            dev["services_resolved"] = utils.dbus_to_python(device["ServicesResolved"])
        if "Appearance" in device:
            dev["appearance"] = utils.dbus_to_python(device["Appearance"])
        if "Paired" in device:
            dev["paired"] = utils.dbus_to_python(device["Paired"])
        if "Connected" in device:
            dev["connected"] = utils.dbus_to_python(device["Connected"])
        if "UUIDs" in device:
            dev["UUIDs"] = utils.dbus_to_python(device["UUIDs"])
        if "RSSI" in device:
            dev["RSSI"] = utils.dbus_to_python(device["RSSI"])
        if "AdvertisingFlags" in device:
            dev["ad_flags"] = utils.byteArrayToHexString(device["AdvertisingFlags"])
        if "ManufacturerData" in device:
            dev["ad_manufacturer_data_cid"] = int(list(device["ManufacturerData"].keys())[0])
            dev["ad_manufacturer_data"] = utils.byteArrayToHexString(
                list(device["ManufacturerData"].values())[0]
            )
        if "ServiceData" in device:
            dev["ad_service_data_uuid"] = utils.dbus_to_python(
                list(device["ServiceData"].keys())[0]
            )
            dev["ad_service_data"] = utils.byteArrayToHexString(
                list(device["ServiceData"].values())[0]
            )
        discovered_devices.append(dev)

    return discovered_devices


def connect(bdaddr):
    bus = dbus.SystemBus()
    device_proxy = general.getDeviceProxy(bus, bdaddr)
    if device_proxy == None:
        return constants.RESULT_ERR_NOT_FOUND
    device_path = device_proxy.object_path
    if not general.is_connected(bus, device_path):
        try:
            device_proxy.Connect()
        except Exception:
            return constants.RESULT_EXCEPTION
        return constants.RESULT_OK
    else:
        return constants.RESULT_OK


def disconnect(bdaddr):
    bus = dbus.SystemBus()
    device_proxy = general.getDeviceProxy(bus, bdaddr)
    device_path = device_proxy.object_path

    if general.is_connected(bus, device_path):
        try:
            device_proxy.Disconnect()
        except Exception:
            return constants.RESULT_EXCEPTION
        return constants.RESULT_OK
    else:
        return constants.RESULT_OK
