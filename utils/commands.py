from dataclasses import dataclass
from typing import Callable

@dataclass(slots=True)
class Command:
    name: str
    function: Callable
    description: str
    category: str   # emoji + category
    label: str     # friendly button label for menus