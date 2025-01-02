class OpenAIException(Exception):
    """Custom exception for OpenAI API errors"""

    def __init__(self, message: str = None):
        super().__init__(message)
        self.message = message
