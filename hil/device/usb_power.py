import dataclasses
from abc import ABC, abstractmethod
from typing import Optional

from hil.utils.YkushAdapter import YkushAdapter


@dataclasses.dataclass
class USBHubPower(ABC):
    enabled: bool
    serial_number: Optional[str] = None
    _adapter: Optional[YkushAdapter] = None

    @abstractmethod
    def power_off(self, dev_path: str) -> None: ...

    @abstractmethod
    def power_on(self, dev_path: str) -> None: ...

    @abstractmethod
    def init(self) -> None: ...


class YKushHubPower(USBHubPower):
    def init(self) -> None:
        self.adapter.enable_all_ports()
        self.adapter.disable_other_boards()

    @property
    def adapter(self) -> YkushAdapter:
        if self._adapter is None:
            self._adapter = YkushAdapter(
                dormant=not self.enabled, serial=self.serial_number
            )
        return self._adapter

    def power_on(self, dev_path: str) -> None:
        # TODO: find ykush port to switch on
        #   repower all ports for now
        self.adapter.enable_all_ports()

    def power_off(self, dev_path: str) -> None:
        # TODO: find ykush port to switch off
        #   disable all ports for now
        self.adapter.disable_all_ports()


class DummyHubPower(YKushHubPower):
    def init(self) -> None:
        pass

    def power_off(self, dev_path: str) -> None:
        pass

    def power_on(self, dev_path: str) -> None:
        pass
