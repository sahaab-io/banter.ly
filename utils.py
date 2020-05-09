import re
from random import randint


def random_color() -> str:
    """
    Generates a color
    :return: a random HEX string between #ffffff and #00000
    """
    return "#" + "%06x" % randint(0, 0xFFFFFF)


def is_hex_color(color: str) -> bool:
    """
    Checks if a given color string is a valid hex color
    :param color:
    :return:
    """
    match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color)
    if not match:
        return False
    return True
