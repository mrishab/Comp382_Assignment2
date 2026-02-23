"""
PDA Controller — mediates between Model and View.

Uses two-phase rendering:
  - render_graph(): full rebuild when PDA changes
  - update_state(): lightweight JS patch on each step
"""


class PushdownAutomataController:
    def __init__(self, model, view, config: dict):
        self.model = model
        self.view = view
        # Full render from the config dict — builds PDABuilder(config) in the view
        self.view.render_graph(config)

    # ── commands ────────────────────────────────────────────────────────────

    def load_input(self, text: str):
        """Load a new input string and reset the automaton."""
        self.model.load_input(text)
        self.view.update_state(self.model)

    def step(self):
        """Execute one transition and refresh the view."""
        if not self.model.is_stuck() and not self.model.is_accepted():
            self.model.step()
        self.view.update_state(self.model)

    def reset(self):
        """Reset to initial configuration (keeps current input)."""
        input_str = self.model.input_string
        self.model.reset()
        self.model.load_input(input_str)
        self.view.update_state(self.model)

    def run_to_end(self):
        """Run all steps until the PDA accepts or gets stuck."""
        while not self.model.is_stuck() and not self.model.is_accepted():
            self.model.step()
        self.view.update_state(self.model)
