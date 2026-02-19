"""
PDA Model — pure data + logic, no UI dependencies.

Transition table format:
  { (state: str, input_symbol: str | None, stack_top: str | None):
    [(next_state: str, stack_push: list[str])] }

  - input_symbol = None  → epsilon (ε) transition on input
  - stack_top    = None  → match any top-of-stack
  - stack_push   = []    → pop without pushing (epsilon push)
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Snapshot:
    """Immutable record of a single configuration before a step."""
    state: str
    stack: list
    input_index: int


class PushdownAutomataModel:
    def __init__(
        self,
        states: set[str],
        alphabet: set[str],
        stack_alphabet: set[str],
        transitions: dict,
        initial_state: str,
        initial_stack_symbol: str,
        final_states: set[str],
    ):
        self.states = states
        self.alphabet = alphabet
        self.stack_alphabet = stack_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol
        self.final_states = final_states
        self.history: list[Snapshot] = []
        self.reset()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self):
        """Return to initial configuration."""
        self.current_state: str = self.initial_state
        self.stack: list[str] = [self.initial_stack_symbol]
        self.input_string: str = ""
        self.input_index: int = 0
        self.history.clear()

    def load_input(self, input_string: str):
        self.reset()
        self.input_string = input_string

    def step(self) -> bool:
        """
        Execute one transition (deterministic: first matching rule wins).
        Returns True if a transition fired, False if stuck.
        """
        char = self.input_string[self.input_index] if self.input_index < len(self.input_string) else None
        stack_top = self.stack[-1] if self.stack else None

        transition = (
            self.transitions.get((self.current_state, char, stack_top))
            or self.transitions.get((self.current_state, None, stack_top))
        )

        if not transition:
            return False

        next_state, stack_push = transition[0]

        # Save snapshot before mutating
        self.history.append(Snapshot(self.current_state, list(self.stack), self.input_index))

        # Consume input only if this was NOT an epsilon transition on input
        if (self.current_state, char, stack_top) in self.transitions and char is not None:
            self.input_index += 1

        # Replace top of stack
        if self.stack:
            self.stack.pop()
        for symbol in reversed(stack_push):
            self.stack.append(symbol)

        self.current_state = next_state
        return True

    def is_accepted(self) -> bool:
        return (
            self.current_state in self.final_states
            and self.input_index == len(self.input_string)
        )

    def is_stuck(self) -> bool:
        """True if no transition is possible from the current configuration."""
        char = self.input_string[self.input_index] if self.input_index < len(self.input_string) else None
        stack_top = self.stack[-1] if self.stack else None
        return not (
            self.transitions.get((self.current_state, char, stack_top))
            or self.transitions.get((self.current_state, None, stack_top))
        )
