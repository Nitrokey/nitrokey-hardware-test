import dataclasses
import logging
import time
import typing
from abc import ABC, abstractmethod
from typing import Sequence

from pynitrokey.trussed.admin_app import BootMode, Variant
from pynitrokey.trussed.bootloader import NitrokeyTrussedBootloader
from pynitrokey.trussed.device import NitrokeyTrussedDevice

from hil.debug_adapter.debug_adapter import DebugAdapter
from hil.device.usb_power import USBHubPower
from hil.exceptions import NoDeviceDetectedException
from hil.provisioner.provision import Provisioner
from hil.runner import Runner
from hil.test_configuration import TestConfiguration

DEVICE_BOOT_TIMEOUT = 90
logger = logging.getLogger(__name__)


@dataclasses.dataclass
class VidPid:
    vid: int
    pid: int


@dataclasses.dataclass
class DeviceProperties:
    usb_id: VidPid
    variant: Variant


@dataclasses.dataclass
class Device(ABC):
    debug_adapter: DebugAdapter
    power_hub: USBHubPower
    runner: Runner
    log: logging.Logger = logger.getChild("device")

    @abstractmethod
    def list_devices(self) -> Sequence[NitrokeyTrussedDevice]: ...

    @abstractmethod
    def properties(self) -> DeviceProperties:
        # TODO get this from config file?
        ...

    @abstractmethod
    def validate_configuration(self, cfg: TestConfiguration) -> None: ...

    def reboot(self) -> bool:
        return self.debug_adapter.reboot()

    # @abstractmethod
    # def id(self) -> str:
    #     ...

    @abstractmethod
    def erase_and_flash_bootloader(self, cfg: TestConfiguration) -> None: ...

    def get_nk3_device(self) -> NitrokeyTrussedDevice:
        dev_list = self.list_devices()
        if len(dev_list) > 1:
            self.log.warning(f"Multiple devices detected: {dev_list}")
        for d in dev_list:
            if d.admin.status().variant == self.properties().variant:
                return d
        raise NoDeviceDetectedException("No device found")

    def shows_up(self) -> None:
        for i in range(DEVICE_BOOT_TIMEOUT + 1):
            dev_list = self.list_devices()

            def log() -> None:
                self.log.debug(
                    f"Getting devs: {dev_list} ({i}/{DEVICE_BOOT_TIMEOUT} seconds passed)"
                )

            if i % 10 == 0:
                log()
            if dev_list:
                log()
                for d in dev_list:
                    if d.admin.status().variant == self.properties().variant:
                        return
            time.sleep(1)
        raise NoDeviceDetectedException("Device does not show up")

    @abstractmethod
    def flash_using_bootloader(self, firmware_path: str) -> None: ...

    def power_cycle(self) -> None:
        self.log.debug("Power cycle")
        self.power_hub.power_off("TODO: path")
        time.sleep(2)
        self.power_hub.power_on("TODO: path")
        # TODO check are the required devices present

    # def flash(self, firmware: str) -> bool:
    #    self.log.debug(f"Flashing {firmware}")
    #    self.try_switch_to_bootloader()
    #    self.flash_using_bootloader(firmware)
    #    return True

    def try_switch_to_bootloader(self) -> None:
        self.log.debug("Switching to bootloader")
        try:
            d = self.get_nk3_device()
            d.admin.reboot(mode=BootMode.BOOTROM)
            time.sleep(2)
        except RuntimeError:
            pass

    def uuid(self) -> str:
        self.log.debug("Getting UUID")
        d = self.get_nk3_device()
        res = str(d.uuid())
        self.log.debug(f"Got UUID {res}")
        return res

    def erase(self) -> None:
        self.log.debug("Calling erase on debug adapter")
        self.debug_adapter.erase()

    def provision(self, provisioner: Provisioner) -> None:
        self.log.debug("Provisioning")
        provisioner.provision()

    @abstractmethod
    def get_bootloader_devices(self) -> typing.Sequence[NitrokeyTrussedBootloader]: ...


@dataclasses.dataclass
class Progress:
    log: logging.Logger = logger.getChild("progress")
    last: int = -1

    def __call__(self, i: int, x: int) -> None:
        self.progress(i, x)

    def progress(self, i: int, x: int) -> None:
        p = 100 * i // x
        if p % 10 == 0 and self.last != p:
            self.last = p
            self.log.info(f"{p}%")
