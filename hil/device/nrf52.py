import time
import typing

from pynitrokey.nk3.bootloader import Nitrokey3BootloaderNrf52
from pynitrokey.trussed.admin_app import Variant

from hil.device.device import DeviceProperties, VidPid
from hil.device.nk3 import NK3Device
from hil.test_configuration import TestConfiguration
from hil.utils.serial_device_manager import get_serial_device_by_name


class NRF52HardwareDevice(NK3Device):
    def validate_configuration(self, cfg: TestConfiguration) -> None:
        # TODO move this to constructor
        assert cfg.variant == "nrf52"
        assert cfg.mbr.path_str.endswith(".hex")
        assert cfg.bootloader.path_str.endswith(".hex")
        assert cfg.provisioner_firmware.path_str.endswith(".hex")
        assert cfg.application_firmware.path_str.endswith(".hex")
        assert cfg.variant in cfg.provisioner_firmware.path_str
        assert cfg.variant in cfg.application_firmware.path_str

    def get_bootloader_devices(self) -> typing.Sequence[Nitrokey3BootloaderNrf52]:
        return Nitrokey3BootloaderNrf52.list()

    def properties(self) -> DeviceProperties:
        return DeviceProperties(usb_id=VidPid(0x20A0, 0x1234), variant=Variant.NRF52)

    def erase_and_flash_bootloader(self, cfg: TestConfiguration) -> None:
        self.debug_adapter.erase_and_flash_bootloader(cfg.mbr, cfg.bootloader)
        self.debug_adapter.reboot()

    def get_serial_device_path(self) -> str:
        # e.g. "/dev/serial/by-id/
        # usb-Nitrokey_Nitrokey_3_Bootloader_F95AF80A9E98-if00"
        # TODO use pynitrokey's bootloader device abstraction instead
        d = None
        for i in range(10):
            d = get_serial_device_by_name("Nitrokey_Nitrokey_3_Bootloader")
            self.log.debug(f"Getting dev: {i} {d}")
            if d:
                break
            time.sleep(1)
        assert d
        return d

    def flash_using_bootloader(self, firmware_path: str) -> None:
        serial_port = self.get_serial_device_path()
        self.debug_adapter.flash_firmware(firmware_path, serial_port)
        self.debug_adapter.reboot()

    # def flash_using_bootloader(self, firmware_path: str) -> None:
    #    def progress(i: int, x: int) -> None:
    #        p = 100 * i // x
    #        if p % 10 == 0:
    #            self.log.info(f"{p}%")
    #    dev_path_alias = self.get_serial_device_path()
    #    assert dev_path_alias
    #    dev_real_path = ExistingFilePath(dev_path_alias).absolute_path_str
    #    device_bootloader = Nitrokey3BootloaderNrf52.open(dev_real_path)
    #    assert device_bootloader
    #    with open(firmware_path, "rb") as f:
    #        firmware_binary = f.read()
    #    assert firmware_binary
    #    device_bootloader.update(firmware_binary, callback=progress)
