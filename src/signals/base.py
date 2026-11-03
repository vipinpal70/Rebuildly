from abc import ABC, abstractmethod
from typing import List

from src.signals.models import Finding, SignalContext


class Detector(ABC):
    """A detector inspects one SignalContext and returns zero or more Findings.

    Return [] when a check could not be performed (lookup failed, data missing) —
    never emit a finding that claims a problem the detector could not verify."""

    name: str = "detector"

    @abstractmethod
    async def detect(self, ctx: SignalContext) -> List[Finding]:
        ...
