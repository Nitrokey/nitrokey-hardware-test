import os
from os.path import join
from typing import Optional

from hil.logs import log

DEV_PATH = "/dev/serial/by-id/"


def get_serial_device_by_name(name: str) -> Optional[str]:
    dev_paths = []
    try:
        dev_paths = os.listdir(DEV_PATH)
        for p in dev_paths:
            if name in p:
                return join(DEV_PATH, p)
    except FileNotFoundError:
        log.warning("No serial devices found")
    log.warning(f'Failed to find serial port name for "{name}". Dev paths: {dev_paths}')
    return None


def test_get_nitrokey3() -> None:
    assert (
        get_serial_device_by_name("Nitrokey_Nitrokey_3_Bootloader")
        == "/dev/serial/by-id/usb-Nitrokey_Nitrokey_3_Bootloader_DE84B34EA6F3-if00"
    ), "This test matches only device with ID DE84B34EA6F3"
