import dataclasses
from abc import ABC, abstractmethod
from typing import Optional

from hil.runner import Runner
from hil.test_configuration import ExistingFilePath, TestConfiguration


@dataclasses.dataclass
class DebugAdapter(ABC):
    runner: Runner
    cfg: TestConfiguration

    @abstractmethod
    def reboot(self) -> bool:
        return True

    @abstractmethod
    def erase_and_flash_bootloader(
        self, mbr: ExistingFilePath, bootloader: ExistingFilePath
    ) -> None: ...

    @abstractmethod
    def erase(self) -> None: ...

    @abstractmethod
    def erase_and_flash(self, firmware: ExistingFilePath) -> None: ...

    def flash_firmware(
        self, firmware_path: str, serial_port: Optional[str] = None
    ) -> None: ...
