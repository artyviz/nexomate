# ai/base.py

from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Abstract AI provider interface.

    Implementations must provide a ``generate`` method that takes a prompt string
    and returns the model's response as a string.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response for the given ``prompt``.

        Args:
            prompt: The text prompt to send to the LLM.
        Returns:
            The generated text.
        """
        raise NotImplementedError
