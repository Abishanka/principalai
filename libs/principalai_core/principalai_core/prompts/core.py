from pydantic import BaseModel
from typing import Optional, Callable

from principalai_core.invocable import Invocable, FunctionInvocable
from principalai_core.language_models import LanguageModel

class Prompt(Invocable):
    """String that will be passed into an LLM. An f-string which is an Invocable and can be run in a language model."""
    def __init__(
        self,
        inputParameterSchema: Optional[BaseModel] = None, 
        outputParameterSchema: Optional[BaseModel] = None,
        languageModel: LanguageModel = None,
        languageModelRunEngine: Callable = None,
        prompt: Optional[str] = None
    ):
        super().__init__(inputParameterSchema, outputParameterSchema, languageModel, languageModelRunEngine)
        self.prompt = prompt

    @property
    def run():
        return None

    @property
    def __str__(self):
        return None


class FunctionPrompt(Prompt, FunctionInvocable):
    """
    Prompts that are implemented as functions.
    Allows for handling variables as function parameters and the prompt f-string in the function body.

    @Prompt
    def prompt_function(name: str, age: int):
        return "Hi, my name is {name}. I am {age} years old"
    """    
    def __init__(
        self,
        inputParameterSchema: Optional[BaseModel] = None, 
        outputParameterSchema: Optional[BaseModel] = None,
        languageModel: LanguageModel = None,
        languageModelRunEngine: Callable = None,
        prompt: Optional[str] = None
    ):
        FunctionInvocable.__init__(self)
        Prompt.__init__(self, inputParameterSchema, outputParameterSchema, languageModel, languageModelRunEngine, prompt)
    
    def run(
        self,
        *args,
        **kwargs
    ):
        completedPrompt = None
        if self.prompt is not None:
            completedPrompt = self.prompt.format(*args, **kwargs)
        else:
            completedPrompt = self.func(*args, **kwargs)
        return self.languageModelRunEngine(completedPrompt)
    
    def __str__(
        self,
        *args,
        **kwargs
    ):
        if self.prompt is not None:
            return self.prompt.format(*args, **kwargs)
        else:
            return self.func(*args, **kwargs)