import os

def load_stylesheet(filename):
    """Loads a stylesheet from the styles directory."""
    style_dir = os.path.join(os.path.dirname(__file__), 'styles')
    path = os.path.join(style_dir, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading stylesheet {filename}: {e}")
        # Returning empty stylesheet to avoid crashing the application
        return ""
