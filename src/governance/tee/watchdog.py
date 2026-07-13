"""
watchdog.py — Heartbeat monitor and deadlock breaker.

Heartbeat watchdog detects compute starvation.
Deadlock breaker detects governance paralysis and triggers cold-boot recovery.
"""

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, List, Optional


class WatchdogState(Enum):
    NORMAL = auto()
    HEARTBEAT_MISSED = auto()
    DEADLOCKED = auto()
    COLD_BOOT = auto()


@dataclass
class WatchdogEvent:
    event_type: str
    timestamp: float
    details: str = ""


class WatchdogTimer:
    def __init__(self, heartbeat_timeout_ms: float = 100.0):
        self.heartbeat_timeout = heartbeat_timeout_ms / 1000.0
        self._last_heartbeat: float = time.time()
        self._state = WatchdogState.NORMAL
        self._events: List[WatchdogEvent] = []

    def heartbeat(self):
        self._last_heartbeat = time.time()
        if self._state == WatchdogState.HEARTBEAT_MISSED:
            self._state = WatchdogState.NORMAL
            self._log("heartbeat_restored", "Heartbeat restored")

    def check(self) -> WatchdogState:
        if self._state == WatchdogState.COLD_BOOT:
            return self._state
        elapsed = time.time() - self._last_heartbeat
        if elapsed > self.heartbeat_timeout:
            if self._state != WatchdogState.HEARTBEAT_MISSED:
                self._state = WatchdogState.HEARTBEAT_MISSED
                self._log("heartbeat_missed",
                          f"Last heartbeat {elapsed:.2f}s ago")
        return self._state

    @property
    def state(self) -> WatchdogState:
        return self._state

    def _log(self, event_type: str, details: str = ""):
        self._events.append(WatchdogEvent(
            event_type=event_type,
            timestamp=time.time(),
            details=details,
        ))

    def get_events(self) -> List[WatchdogEvent]:
        return list(self._events)


class DeadlockBreaker:
    def __init__(self, threshold_cycles: int = 100):
        self.threshold = threshold_cycles
        self._cycles_without_decision: int = 0
        self._cold_boot_triggered: bool = False
        self._total_cold_boots: int = 0

    def record_cycle(self, decision_produced: bool):
        if self._cold_boot_triggered:
            return
        if decision_produced:
            self._cycles_without_decision = 0
        else:
            self._cycles_without_decision += 1

    def check(self) -> bool:
        if self._cold_boot_triggered:
            return False
        if self._cycles_without_decision >= self.threshold:
            self._cold_boot_triggered = True
            self._total_cold_boots += 1
            return True
        return False

    def reset(self):
        self._cycles_without_decision = 0
        self._cold_boot_triggered = False

    @property
    def is_deadlocked(self) -> bool:
        return self._cycles_without_decision >= self.threshold

    @property
    def stalled_cycles(self) -> int:
        return self._cycles_without_decision

    @property
    def total_cold_boots(self) -> int:
        return self._total_cold_boots
