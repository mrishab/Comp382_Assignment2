"""
PDA Controller — mediates between Model and View.
"""


class PushdownAutomataController:

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.update_view(self.model)

    # ── commands ────────────────────────────────────────────────────────────

    def load_input(self, text: str):
        """Load a new input string and reset the automaton."""
        self.model.load_input(text)
        self.view.update_view(self.model)

    def step(self):
        """Execute one transition and refresh the view."""
        if not self.model.is_stuck() and not self.model.is_accepted():
            self.model.step()
        self.view.update_view(self.model)

    def reset(self):
        """Reset to initial configuration (keeps current input)."""
        input_str = self.model.input_string
        self.model.reset()
        self.model.load_input(input_str)
        self.view.update_view(self.model)

    def run_to_end(self):
        """Run all steps until the PDA accepts or gets stuck."""
        while not self.model.is_stuck() and not self.model.is_accepted():
            self.model.step()
        self.view.update_view(self.model)