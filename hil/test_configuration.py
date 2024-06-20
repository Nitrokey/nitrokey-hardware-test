import dataclasses
import logging
import pathlib
import tomllib
from pathlib import Path

log = logging.getLogger(__name__)


@dataclasses.dataclass
class ExistingFilePath:
    _path: Path

    def __init__(self, path: str):
        assert path, f"Path string is empty: {path}"
        if "*" not in path:
            self._path = pathlib.Path(path)
        else:
            matches = list(pathlib.Path(path).parent.glob(pathlib.Path(path).name))
            assert (
                len(matches) == 1
            ), f"No unique match found for path {path}: {matches}"
            self._path = matches[0]
            log.debug(f"Selecting {matches[0]} for expression: {path}")
        log.debug(f"Testing if path exists: {path}")
        assert self._path.exists(), f"The path {self.path_str} does not exist"

    @property
    def path_str(self) -> str:
        return str(self._path)

    @property
    def absolute_path_str(self) -> str:
        return str(self._path.absolute().resolve())


@dataclasses.dataclass
class TestConfiguration:
    device: str
    provisioner_firmware: ExistingFilePath
    application_firmware: ExistingFilePath
    firmware_version: str
    mbr: ExistingFilePath
    bootloader: ExistingFilePath
    bootloader_key: ExistingFilePath
    fido_key_path: ExistingFilePath
    fido_certificate_path: ExistingFilePath
    usb_manager_enabled: bool
    variant: str  # TODO use enum for specifying variants, and a proper parsing
    output: str
    ykush_port_device: int
    ykush_port_debug_adapter: int
    ykush_serial_number: str
    test_fido2: bool
    test_secrets: bool
    test_opcard: bool

    @classmethod
    def from_config_file(cls, p: ExistingFilePath) -> "TestConfiguration":
        with open(p.path_str, "r") as f:
            data = f.read()
        config = tomllib.loads(data)
        # FIXME replace with automatic loading, e.g. using pydantic
        return TestConfiguration(
            device=config["device"],
            provisioner_firmware=ExistingFilePath(config["provisioner_firmware"]),
            application_firmware=ExistingFilePath(config["application_firmware"]),
            firmware_version="",
            mbr=ExistingFilePath(config["mbr"]),
            bootloader=ExistingFilePath(config["bootloader"]),
            bootloader_key=ExistingFilePath(config["bootloader_key"]),
            fido_key_path=ExistingFilePath(config["fido_key_path"]),
            fido_certificate_path=ExistingFilePath(config["fido_certificate_path"]),
            # TODO validate variants and bool values
            usb_manager_enabled=config["usb_manager_enabled"],
            variant=config["variant"],
            output=config["output"],
            # TODO validate port numbers
            ykush_port_device=config["ykush_port_device"],
            ykush_port_debug_adapter=config["ykush_port_debug_adapter"],
            ykush_serial_number=config["ykush_serial_number"],
            test_fido2=config["test_fido2"],
            test_secrets=config["test_secrets"],
            test_opcard=config["test_opcard"],
        )
