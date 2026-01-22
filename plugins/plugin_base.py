from abc import ABC, abstractmethod
from telepot import Bot
from collections.abc import Callable
from typing import Any

class Plugin(ABC):
    def __init__(self, button_label: str, command: str, descritpion: str):
        self.button_label = button_label
        self.command = command
        self.description = descritpion
        self.bot: Bot | None = None

    def bind_bot(self, bot: Bot):
        self.bot = bot

    def bind_pep(self, pep2: Any):
        self.pep2 = pep2

    @abstractmethod
    def action(self, *args) -> None:
        pass

    def export(self) -> dict[str, tuple[str, Callable]]:
        return {
            self.button_label: (self.command, self.action, self.description)
        }