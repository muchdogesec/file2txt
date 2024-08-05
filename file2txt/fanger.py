import re


class Fanger:
    """Load a list of texts and provide functionality for defanging."""

    def __init__(self, input_text: str):
        """Initialize Fanger with a list of texts."""
        self.input_text = input_text

    def defang(self) -> list:
        """Defang each text in the list and return the list."""
        return self._apply_replacements_to_text(self.input_text)

    @staticmethod
    def _apply_replacements_to_text(text: str) -> str:
        """Apply defang replacements to a single text."""

        # Define the replacements
        replacements = [
            (r'hxxp', 'http'),
            (r'\{dot\}', '.'),
            (r'\[dot\]', '.'),
            (r'\(dot\)', '.'),
            (r'\{at\}', '@'),
            (r'\[at\]', '@'),
            (r'\(at\)', '@'),
            (r'\{:\}', ':'),
            (r'\[:\]', ':'),
            (r'\(:\)', ':'),
            # Remove bracketing characters
            (r'\[(\.|@|/|\\|://|:)\]', r'\1'),  # square brackets
            (r'\{(\.|@|/|\\|://|:)\}', r'\1'),  # curly brackets
            (r'\((\.|@|/|\\|://|:)\)', r'\1'),  # parentheses
            # Remove spaces around specific characters
            (r'\s?(\.|@|/|\\|://|:)\s?', r'\1')
        ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
        return text
