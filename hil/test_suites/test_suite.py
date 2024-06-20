import dataclasses
import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from hil.runner import Runner
from hil.test_configuration import TestConfiguration

log = logging.getLogger(__name__)


# TODO make it abstract, and do separate classes for Success and failure
@dataclasses.dataclass
class TestResult:
    output: List[str]

    def ok(self) -> bool:
        return "OK" in self.output

    def fail(self) -> bool:
        return not self.ok()


@dataclasses.dataclass
class TestSuite(ABC):
    runner: Runner
    artifacts_destination_path: str
    cfg: TestConfiguration

    @abstractmethod
    def get_artifacts_list(self) -> List[str]:
        """Specify list of the artifact paths to collect"""
        ...

    @abstractmethod
    def execute(self, uuid: str) -> TestResult:
        """Define how the test should be executed"""
        ...

    def name(self) -> str:
        """Specify test name"""
        return self.__class__.__name__

    def collect_artifacts(self) -> None:
        """
        Collect all the additional results of the tests, like resulting files,
        snapshots of the file system, etc.
        """
        log.debug("Collecting artifacts")
        target = Path(self.artifacts_destination_path) / Path(self.name())
        if not target.exists():
            target.mkdir(parents=True)
        for artifact_path_str in self.get_artifacts_list():
            artifact_path = Path(artifact_path_str)
            if not artifact_path.exists():
                log.warning(f"Artifact under path {artifact_path_str} does not exist")
                continue
            shutil.copy(
                str(artifact_path.absolute().resolve()),
                str(target.absolute().resolve()),
            )
