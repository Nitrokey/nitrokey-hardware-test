import typing

from pynitrokey.nk3.bootloader import Nitrokey3BootloaderLpc55
from pynitrokey.trussed.admin_app import Variant

from hil.device.device import DeviceProperties, VidPid
from hil.device.nk3 import NK3Device
from hil.test_configuration import ExistingFilePath, TestConfiguration


class LPC55HardwareDevice(NK3Device):
    def validate_configuration(self, cfg: TestConfiguration) -> None:
        assert cfg.variant == "lpc55"
        assert cfg.provisioner_firmware.path_str.endswith(".bin")
        assert cfg.application_firmware.path_str.endswith(".bin")
        assert cfg.variant in cfg.provisioner_firmware.path_str
        assert cfg.variant in cfg.application_firmware.path_str

    def get_bootloader_devices(self) -> typing.Sequence[Nitrokey3BootloaderLpc55]:
        return Nitrokey3BootloaderLpc55.list()

    def properties(self) -> DeviceProperties:
        return DeviceProperties(
            usb_id=VidPid(0x20A0, 0x1234),
            variant=Variant.LPC55,
        )

    def erase_and_flash_bootloader(self, cfg: TestConfiguration) -> None:
        # Using vendor's bootloader, nothing to do
        pass

    def flash_using_bootloader(self, firmware_path: str) -> None:
        self.debug_adapter.erase_and_flash(ExistingFilePath(firmware_path))

        # raise DeprecatedException("Should not be used")
        # with open(firmware_path, "rb") as f:
        #    firmware_binary = f.read()
        # assert firmware_binary
        # bootloader_list = self.get_bootloader_devices()
        # assert bootloader_list
        # b = bootloader_list[0]
        ## b.update(firmware_binary, progress)
        # assert isinstance(b, Nitrokey3BootloaderLpc55)
        ## b: Nitrokey3BootloaderLpc55
        ## b.device: McuBoot
        # with b.device as mcuboot:
        #    mcuboot.write_memory(0, firmware_binary, progress_callback=Progress())
        #    # mcuboot.load_image()
        #    mcuboot.reset(timeout=10, reopen=True)

    ## FIXME do not use str, but existingfilepath
    # def flash(self, firmware: str) -> bool:
    #    self.log.debug(f"Flashing {firmware}")
    #    self.debug_adapter.erase_and_flash(ExistingFilePath(firmware))
    #    return True
