from typing import List

from hil.test_suites.test_suite import TestResult, TestSuite


class FullTestSuite(TestSuite):
    """Runner for the Full Test Suite from nitrokey-3-tests"""

    def get_artifacts_list(self) -> List[str]:
        return [
            "tests/nitrokey-3-tests/report-full.html",
            "tests/nitrokey-3-tests/report-junit-full.xml",
        ]

    def execute(self, uuid: str) -> TestResult:
        model = self.cfg.device
        cmds = f"""
        make -C tests/nitrokey-3-tests/ run-hw ALLOWED_UUIDS={uuid} DOCKER=podman NK_MODEL={model} TEST_SUITE=full PYTEST_EXTRA='--hil --durations=0 -o log_cli=false -o log_cli_level=debug -W ignore::DeprecationWarning --template=html1/index.html --report report-full.html --junitxml=report-junit-full.xml'<< EOF
        """.strip()
        err = None
        try:
            for cmd in cmds.splitlines():
                self.runner(cmd)
        except Exception as e:
            err = e
        if err:
            return TestResult([f"Fail: {err}"])
        return TestResult(["OK"])
