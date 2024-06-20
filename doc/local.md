# Running hil locally

**Note:** Currently only works with NK3 variants and not with NKPK!

If starting a full run of hil in CI is not necessary or unfeasible, it is possible to run hil locally on one device at a time.

## Requirements
### Hardware
Essentially the same hardware as described in [Bill of Materials](/doc/hardware.md#hardware-bill-of-materials) except for the YKush 3 USB Hub:

- LPC55 setup:
  - 1x Nitrokey 3A NFC or Nitrokey 3C NFC
  - 1x NXP LPC-Link 2
  - 1x ADAFRUIT SWD breakout


- NRF52 setup:
  - 1x Nitrokey 3A Mini
  - 1x Nordic NRF52840-DK
  - 1x NK3A Mini Production Header

Please follow [Hardware Setup](/doc/hardware.md) for further setup.
### Software
`nitropy` is used to detect the type of the connected Key:
- `pip install pynitrokey`

Local hil runs on either docker or podman. If podman is to be used, make sure sufficient permissions are granted. Otherwise docker has proven to work more reliably on some systems.

To build the used image with podman:
- `make build_local`

To build the used image with docker:
- `make build_local_docker`

## Usage
- Since the local hil is not executed from CI, the firmware and provisioner files need to be provided manually in a directory called `artifacts`.
- Before running make sure only the one Security Key to be tested is connected. The following script also ensures this.
- Also make sure the key and the developer board are both connected to the local machine.

To run local hil with podman:
- `make run_local`

To run local hil with docker:
- `make run_local_docker`
