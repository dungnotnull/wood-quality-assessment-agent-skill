"""
Wood Quality Assessment - Hooks System
Implements lifecycle hooks, state management, and event emission for skills.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from threading import RLock
from typing import (
    Any,
    TypeVar,
)

# Type aliases
HookFunc = Callable[..., Any]
HookContext = dict[str, Any]
T = TypeVar("T")

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("wqa.hooks")


class HookPoint(Enum):
    """Enumeration of all hook points in the skill lifecycle."""

    BEFORE_SKILL_INVOKE = "before_skill_invoke"
    AFTER_SKILL_INVOKE = "after_skill_invoke"
    ON_SKILL_ERROR = "on_skill_error"
    BEFORE_QUALITY_GATE = "before_quality_gate"
    AFTER_QUALITY_GATE = "after_quality_gate"
    STATE_CHANGE = "state_change"
    KNOWLEDGE_UPDATE = "knowledge_update"
    DEGRADATION_TRIGGERED = "degradation_triggered"


@dataclass
class HookEvent:
    """Represents a single hook event."""

    hook_point: HookPoint
    timestamp: datetime
    skill_name: str
    data: dict[str, Any] = field(default_factory=dict)
    execution_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "hook_point": self.hook_point.value,
            "timestamp": self.timestamp.isoformat(),
            "skill_name": self.skill_name,
            "data": self.data,
            "execution_id": self.execution_id,
        }


@dataclass
class SkillState:
    """Persistent state for a skill execution."""

    skill_name: str
    execution_id: str
    started_at: datetime
    status: str = "pending"
    current_step: int = 0
    total_steps: int = 8
    gates_passed: list[str] = field(default_factory=list)
    gates_failed: list[str] = field(default_factory=list)
    degradation_level: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "skill_name": self.skill_name,
            "execution_id": self.execution_id,
            "started_at": self.started_at.isoformat(),
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "gates_passed": self.gates_passed,
            "gates_failed": self.gates_failed,
            "degradation_level": self.degradation_level,
            "metadata": self.metadata,
        }


class HookRegistry:
    """Registry for hook functions."""

    _instance: HookRegistry | None = None
    _lock = RLock()

    def __new__(cls) -> HookRegistry:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._hooks: dict[HookPoint, list[HookFunc]] = {}
                    cls._instance._event_log: list[HookEvent] = []
        return cls._instance

    def register(self, hook_point: HookPoint, func: HookFunc) -> None:
        """Register a hook function for a given hook point."""
        with self._lock:
            if hook_point not in self._hooks:
                self._hooks[hook_point] = []
            self._hooks[hook_point].append(func)
            logger.info(f"Registered hook for {hook_point.value}: {func.__name__}")

    def unregister(self, hook_point: HookPoint, func: HookFunc) -> None:
        """Unregister a hook function."""
        with self._lock:
            if hook_point in self._hooks and func in self._hooks[hook_point]:
                self._hooks[hook_point].remove(func)
                logger.info(f"Unregistered hook for {hook_point.value}: {func.__name__}")

    def get_hooks(self, hook_point: HookPoint) -> list[HookFunc]:
        """Get all registered hooks for a hook point."""
        with self._lock:
            return self._hooks.get(hook_point, []).copy()

    def emit(self, event: HookEvent) -> None:
        """Emit an event to all registered hooks."""
        hooks = self.get_hooks(event.hook_point)
        for hook in hooks:
            try:
                hook(event)
            except Exception as e:
                logger.error(f"Hook error for {event.hook_point.value}: {e}")

        # Log event
        with self._lock:
            self._event_log.append(event)

    def get_event_log(self, since: datetime | None = None) -> list[HookEvent]:
        """Get event log, optionally filtered by time."""
        with self._lock:
            if since is None:
                return self._event_log.copy()
            return [e for e in self._event_log if e.timestamp >= since]


class StateManager:
    """Manages persistent state for skill executions."""

    def __init__(self, state_file: Path = Path(".state/skill_state.json")):
        self.state_file = state_file
        self._states: dict[str, SkillState] = {}
        self._lock = RLock()
        self._ensure_state_dir()

    def _ensure_state_dir(self) -> None:
        """Ensure state directory exists."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def _generate_execution_id(self, skill_name: str) -> str:
        """Generate unique execution ID."""
        timestamp = datetime.now().isoformat()
        seed = f"{skill_name}:{timestamp}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

    def create_state(self, skill_name: str, total_steps: int = 8) -> SkillState:
        """Create a new skill execution state."""
        execution_id = self._generate_execution_id(skill_name)
        state = SkillState(
            skill_name=skill_name,
            execution_id=execution_id,
            started_at=datetime.now(),
            total_steps=total_steps,
        )
        with self._lock:
            self._states[execution_id] = state
        return state

    def get_state(self, execution_id: str) -> SkillState | None:
        """Get state by execution ID."""
        with self._lock:
            return self._states.get(execution_id)

    def update_state(self, execution_id: str, **updates: Any) -> bool:
        """Update state fields."""
        with self._lock:
            if execution_id not in self._states:
                return False
            state = self._states[execution_id]
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            return True

    def persist(self) -> None:
        """Persist states to disk."""
        with self._lock:
            states_data = {exec_id: state.to_dict() for exec_id, state in self._states.items()}
            self.state_file.write_text(json.dumps(states_data, indent=2), encoding="utf-8")
            logger.debug(f"Persisted {len(states_data)} states to {self.state_file}")

    def load(self) -> None:
        """Load states from disk."""
        if not self.state_file.exists():
            return

        with self._lock:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            self._states = {}
            for exec_id, state_dict in data.items():
                state = SkillState(
                    skill_name=state_dict["skill_name"],
                    execution_id=state_dict["execution_id"],
                    started_at=datetime.fromisoformat(state_dict["started_at"]),
                    status=state_dict.get("status", "pending"),
                    current_step=state_dict.get("current_step", 0),
                    total_steps=state_dict.get("total_steps", 8),
                    gates_passed=state_dict.get("gates_passed", []),
                    gates_failed=state_dict.get("gates_failed", []),
                    degradation_level=state_dict.get("degradation_level", 0),
                    metadata=state_dict.get("metadata", {}),
                )
                self._states[exec_id] = state
            logger.debug(f"Loaded {len(self._states)} states from {self.state_file}")


# Global instances
hook_registry = HookRegistry()
state_manager = StateManager()


def hook(hook_point: HookPoint) -> Callable[[HookFunc], HookFunc]:
    """Decorator to register a function as a hook."""

    def decorator(func: HookFunc) -> HookFunc:
        hook_registry.register(hook_point, func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def skill_execution(skill_name: str, total_steps: int = 8) -> Iterator[HookContext]:
    """Context manager for skill execution with automatic hooks."""
    execution_id = state_manager._generate_execution_id(skill_name)
    state = state_manager.create_state(skill_name, total_steps)

    context = {
        "skill_name": skill_name,
        "execution_id": execution_id,
        "state": state,
        "start_time": time.time(),
    }

    # Emit before skill invoke hook
    before_event = HookEvent(
        hook_point=HookPoint.BEFORE_SKILL_INVOKE,
        timestamp=datetime.now(),
        skill_name=skill_name,
        data={"execution_id": execution_id},
        execution_id=execution_id,
    )
    hook_registry.emit(before_event)

    state.status = "running"
    state_manager.update_state(execution_id, status="running")

    try:
        yield context

        # Emit after skill invoke hook
        duration_ms = (time.time() - context["start_time"]) * 1000
        after_event = HookEvent(
            hook_point=HookPoint.AFTER_SKILL_INVOKE,
            timestamp=datetime.now(),
            skill_name=skill_name,
            data={"execution_id": execution_id, "duration_ms": duration_ms, "success": True},
            execution_id=execution_id,
        )
        hook_registry.emit(after_event)

        state.status = "completed"
        state_manager.update_state(execution_id, status="completed")

    except Exception as e:
        # Emit error hook
        error_event = HookEvent(
            hook_point=HookPoint.ON_SKILL_ERROR,
            timestamp=datetime.now(),
            skill_name=skill_name,
            data={"execution_id": execution_id, "error": str(e), "error_type": type(e).__name__},
            execution_id=execution_id,
        )
        hook_registry.emit(error_event)

        state.status = "failed"
        state_manager.update_state(execution_id, status="failed", metadata={"error": str(e)})
        raise
    finally:
        state_manager.persist()


@contextmanager
def quality_gate(gate_name: str, execution_id: str, skill_name: str) -> Iterator[HookContext]:
    """Context manager for quality gate execution with hooks."""
    context = {
        "gate_name": gate_name,
        "execution_id": execution_id,
        "skill_name": skill_name,
        "start_time": time.time(),
    }

    # Emit before quality gate hook
    before_event = HookEvent(
        hook_point=HookPoint.BEFORE_QUALITY_GATE,
        timestamp=datetime.now(),
        skill_name=skill_name,
        data={"gate": gate_name, "execution_id": execution_id},
        execution_id=execution_id,
    )
    hook_registry.emit(before_event)

    try:
        yield context
    finally:
        duration_ms = (time.time() - context["start_time"]) * 1000

        # Emit after quality gate hook
        after_event = HookEvent(
            hook_point=HookPoint.AFTER_QUALITY_GATE,
            timestamp=datetime.now(),
            skill_name=skill_name,
            data={"gate": gate_name, "execution_id": execution_id, "duration_ms": duration_ms},
            execution_id=execution_id,
        )
        hook_registry.emit(after_event)


def emit_state_change(execution_id: str, skill_name: str, changes: dict[str, Any]) -> None:
    """Emit a state change event."""
    event = HookEvent(
        hook_point=HookPoint.STATE_CHANGE,
        timestamp=datetime.now(),
        skill_name=skill_name,
        data={"execution_id": execution_id, "changes": changes},
        execution_id=execution_id,
    )
    hook_registry.emit(event)


def emit_degradation(
    execution_id: str, skill_name: str, degradation_level: int, reason: str
) -> None:
    """Emit a degradation triggered event."""
    event = HookEvent(
        hook_point=HookPoint.DEGRADATION_TRIGGERED,
        timestamp=datetime.now(),
        skill_name=skill_name,
        data={
            "execution_id": execution_id,
            "degradation_level": degradation_level,
            "reason": reason,
        },
        execution_id=execution_id,
    )
    hook_registry.emit(event)


def emit_knowledge_update(section: str, entries_added: int, source: str) -> None:
    """Emit a knowledge base update event."""
    event = HookEvent(
        hook_point=HookPoint.KNOWLEDGE_UPDATE,
        timestamp=datetime.now(),
        skill_name="knowledge_updater",
        data={"section": section, "entries_added": entries_added, "source": source},
        execution_id="",
    )
    hook_registry.emit(event)


# Built-in hooks


@hook(HookPoint.BEFORE_SKILL_INVOKE)
def log_skill_invoke(event: HookEvent) -> None:
    """Log skill invocation."""
    logger.info(f"Skill invoke: {event.skill_name} (ID: {event.execution_id})")


@hook(HookPoint.ON_SKILL_ERROR)
def log_skill_error(event: HookEvent) -> None:
    """Log skill errors."""
    error = event.data.get("error", "Unknown error")
    logger.error(f"Skill error: {event.skill_name} - {error}")


@hook(HookPoint.DEGRADATION_TRIGGERED)
def log_degradation(event: HookEvent) -> None:
    """Log degradation events."""
    level = event.data.get("degradation_level", 0)
    reason = event.data.get("reason", "Unknown")
    logger.warning(f"Degradation level {level} triggered: {event.skill_name} - {reason}")


# Example usage and testing
if __name__ == "__main__":
    # Test the hooks system
    print("Testing Wood Quality Assessment Hooks System")
    print("=" * 60)

    # Custom hook example
    @hook(HookPoint.AFTER_SKILL_INVOKE)
    def custom_after_hook(event: HookEvent) -> None:
        print(f"Custom hook triggered after {event.skill_name}")

    # Test skill execution
    with skill_execution("test-skill", total_steps=5) as ctx:
        print(f"Executing skill: {ctx['skill_name']}")
        print(f"Execution ID: {ctx['execution_id']}")

        # Simulate step
        state_manager.update_state(ctx["execution_id"], current_step=1)
        emit_state_change(ctx["execution_id"], ctx["skill_name"], {"current_step": 1})

        # Test quality gate
        with quality_gate("U1", ctx["execution_id"], ctx["skill_name"]) as gate_ctx:
            print(f"Executing gate: {gate_ctx['gate_name']}")
            state_manager.update_state(ctx["execution_id"], gates_passed=["U1"])

    # Check event log
    print("\nEvent Log:")
    events = hook_registry.get_event_log()
    for event in events:
        print(f"  {event.hook_point.value}: {event.skill_name}")

    # Check state
    state = state_manager.get_state(ctx["execution_id"])
    if state:
        print("\nFinal State:")
        print(f"  Status: {state.status}")
        print(f"  Gates passed: {state.gates_passed}")
        print(f"  Current step: {state.current_step}/{state.total_steps}")

    print("\nHooks system test completed successfully!")
