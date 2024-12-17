from openai import (
    OpenAI as OpenAIBase,
    AsyncOpenAI as AsyncOpenAIBase
)

from principalai_core.language_models import LanguageModel

class OpenAI_(LanguageModel):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.provider = OpenAIBase(*args, **kwargs)
        self.providerName = "OpenAI"
    
    def run():
        pass

class AsyncOpenAI_(LanguageModel):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.provider = AsyncOpenAIBase(*args, **kwargs)
        self.providerName = "OpenAI"
        self.asynchronous = True
    
    def run():
        pass