import dataclasses
from abc import ABC, abstractmethod
from typing import Optional

from hil.runner import Runner
from hil.test_configuration import ExistingFilePath


@dataclasses.dataclass
class ProvisionConfiguration:
    fido_key_path: ExistingFilePath
    fido_certificate_path: ExistingFilePath
    device: str
    device_id: Optional[str]


@dataclasses.dataclass
class Provisioner(ABC):
    cfg: ProvisionConfiguration
    runner: Runner

    @abstractmethod
    def provision(self) -> None: ...
