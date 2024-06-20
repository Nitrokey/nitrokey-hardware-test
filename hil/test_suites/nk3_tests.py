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
        # needs reactivate once all tests are working (ssh)
        # cmd = f"""
        # make -C tests/nitrokey-3-tests/ run-hw-report ALLOWED_UUIDS={uuid} DOCKER=podman << EOF
        # """
        # test_pat = "test_fido2 or test_secrets or test_list or test_lsusb"
        tests = ["test_list", "test_lsusb", "test_nk3"]
        if self.cfg.test_fido2:
            tests.append("test_fido2")
        if self.cfg.test_secrets:
            tests.append("test_secrets")
        if self.cfg.test_opcard:
            tests.append("test_opcard")
        test_pat = " or ".join(tests)
        cmd = f"""
        make -C tests/nitrokey-3-tests/ run-hw ALLOWED_UUIDS={uuid} DOCKER=podman PYTEST_EXTRA="--template=html1/index.html --report report.html --junitxml=report-junit.xml -k '{test_pat}'" << EOF
        """

        err = None
        try:
            self.runner(cmd)
        except Exception as e:
            err = e
        if err:
            return TestResult([f"Fail: {err}"])
        return TestResult(["OK"])
