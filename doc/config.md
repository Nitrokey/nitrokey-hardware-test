# Configure hardware
In order for the hil to know where to find Devices Under Test (DUT), they need to be configured.

Each DUT needs its own configuration under `config/DUT_NAME/config.toml`. 

Take current configuration as example and change at least the YKush serial number to your specific setup.

## Changing YKush serial number
Each YKush device has a unique serial number. The hil uses these to enable or disable the connection of specific DUTs as needed.
This is configured under `ykush_serial_number` in each DUTs `config.toml`.

Use the `ykushcmd` tool to find out this serial number:

1. Make sure you have only one YKush device connected 
2. Enter the running container set up in [deploy](/doc/deploy.md)
    - `make gl-runner-enter`
3. Execute `ykushcmd ykush3 -l`
4. This shuould output the serial number of the connected 
5. Enter the serial number in the `config.toml` for the device you connect to this YKush device

## Bootloader and mbr
NRF52 devices need nrf and bootloaders configured.

Example bootloaders for Nitrokey 3A mini and Nitrokey Passkey can be found in the example configuration.

## Run hil in CI
In the job script of your ci clone this repository and start the hil with the following command for a specific DUT and tests:

`make -C nitrokey-hardware-test ci FW=../artifacts MODEL=$DUT TESTS=$TESTS`
