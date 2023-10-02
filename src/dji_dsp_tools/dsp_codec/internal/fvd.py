""" FirmwareVersionDependency enum """


class FirmwareVersionDependency:
    """ FirmwareVersionDependency enum """
    def __init__(self,
                 part1: int = 0,
                 part2: int = 0,
                 part3: int = 0):
        self.value = f"{part1:0<2d}.{part2:0<2d}.{part3:0<4d}"


def get_fvd_from_string(firmware_version_dependency_string: str) -> FirmwareVersionDependency:
    """ Get FirmwareVersionDependency from string """
    return FirmwareVersionDependency(*map(int, firmware_version_dependency_string.split(".")))
