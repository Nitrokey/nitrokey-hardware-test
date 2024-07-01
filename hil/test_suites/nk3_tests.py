from typing import List

from hil.test_suites.test_suite import TestResult, TestSuite


class Nitrokey3TestSuite(TestSuite):
    """Runner for the Nitrokey 3 Test Suite"""

    def get_artifacts_list(self) -> List[str]:
        return [
            "tests/nitrokey-3-tests/report.html",
            "tests/nitrokey-3-tests/report-junit.xml",
        ]

    def execute(self, uuid: str) -> TestResult:
        model = self.cfg.device
        cmd = f"""
        make -C tests/nitrokey-3-tests/ run-hw-report ALLOWED_UUIDS={uuid} DOCKER=podman NK_MODEL={model} TEST_SUITE=normal PYTEST_EXTRA='--hil' << EOF
        """

        err = None
        try:
            self.runner(cmd)
        except Exception as e:
            err = e
        if err:
            return TestResult([f"Fail: {err}"])
        return TestResult(["OK"])
