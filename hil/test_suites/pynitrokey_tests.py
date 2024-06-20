import logging
import os
import tempfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, List, Optional

from hil.test_suites.test_suite import TestResult, TestSuite


class pynitrokeyTestSuite(TestSuite):
    """Runner for pynitrokey test suite"""

    tmpFilePath: Optional[Path] = None
    tmpDir: Optional[TemporaryDirectory[Any]] = None
    logger = logging.getLogger(__name__)

    def get_artifacts_list(self) -> List[str]:
        return [str(self.tmpFilePath)]

    def __del__(self) -> None:
        self.logger.debug(f"Removing {self.tmpFilePath}")
        if self.tmpFilePath and self.tmpFilePath.exists():
            self.tmpFilePath.unlink()
        # tmpFilePath should be removed automatically

    def execute(self, uuid: str) -> TestResult:
        self.tmpDir = tempfile.TemporaryDirectory()
        self.tmpFilePath = Path(os.path.join(self.tmpDir.name, "output.txt"))

        # nitropy nk3 test > {str(self.tmpFilePath)} << EOF
        cmd = f"""
        nitropy {self.cfg.device} test --only uuid,version,status
        """
        err = None
        try:
            self.runner(cmd, save_output_to=str(self.tmpFilePath))
        except Exception as e:
            err = e
        if err:
            return TestResult([f"Fail: {err}"])
        return TestResult(["OK"])
