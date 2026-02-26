from abc import ABC, abstractmethod

from algorepo.models import Problem


#WAITING: Add Config argument for platform initialization
class Platform(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def fetch(self, url: str) -> dict:
        """Network request
        Input: URL adress form request
        Output: Raw platform data"""

    @abstractmethod
    def parse(self, raw: dict, url: str) -> Problem:
        """Problem parser
        Input: Raw problem data
        Return: Ready to solve Problem
        """
