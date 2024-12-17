from typing import Optional, Any

class LanguageModel():
    def __init__(self):
        self.provider: Optional[Any]  = None
        self.providerName: Optional[str] = None
        self.model: Optional[str] = None
        self.asynchronous: bool = False

    def run():
        return None