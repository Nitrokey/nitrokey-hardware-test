# Nitrokey Hardware Tests

Automatic Test Executor on real hardware

Deploy and test firmware directly through the CI, and get a complete report, with information about potential
regressions.

Features:

- abstracted test suites
- abstracted hardware configuration
- automatic artifacts collection
- isolated run in a container, without a need for root
- executing as a Gitlab Runner
- configuration check at start-up
- real time kernel messages logger
- local run (NK3 only): ykush manual emulation mode (to have the whole solution running locally)

## Usage

- [Set up hardware](/doc/hardware.md)
- [Deploy the gitlab runner](/doc/deploy.md)
- [Configure hardware](/doc/config.md)
- [Local hil (NK3 only)](/doc/local.md)

## Architecture / Development

The main test loop is executed over the injected components,
chosen accordingly to the details specified in the configuration.


Component types:
- debug adapter (`hil/debug_adapter`) - responsible for calls to the debug adapter software, realizing flashing, erasing, and state download
- device manager ("device", `hil/device`) - manages all high-level device's operations, called from the test suite
- provisioner (`hil/provisioner`) - configures device for use with the main application
- test suite (`hil/test_suite`) - executes the test suites, and gathers results

The solution uses pynitrokey for bootloader interactions where needed.

Extensibility is provided by implementing the required functions set by the parent abstract classes.
This could be further improved by using any Python plugin framework like [pluggy](https://pluggy.readthedocs.io/en/latest/).

