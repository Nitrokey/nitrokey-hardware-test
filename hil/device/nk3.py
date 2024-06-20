from typing import Sequence

from pynitrokey.nk3.device import Nitrokey3Device

from hil.device.device import Device


class NK3Device(Device):
    def list_devices(self) -> Sequence[Nitrokey3Device]:
        return Nitrokey3Device.list()
