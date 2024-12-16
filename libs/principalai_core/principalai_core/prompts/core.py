from pydantic import BaseModel
from typing import Optional, Callable

from principalai_core.invocable.core import Invocable, FunctionInvocable

class Prompt(Invocable):
    """String that will be passed into an LLM. An f-string which is an Invocable and can be run in a language model."""
    def __init__(
        self,
        inputParameterSchema_: Optional[BaseModel] = None, 
        outputParameterSchema_: Optional[BaseModel] = None,
        prompt_: Optional[str] = None
    ):
        super().__init(inputParameterSchema_, outputParameterSchema_)
        self.prompt = prompt_

    @property
    def run():
        pass

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
        inputParameterSchema_: Optional[BaseModel] = None, 
        outputParameterSchema_: Optional[BaseModel] = None,
        prompt_: Optional[str] = None
    ):
        super().__init(inputParameterSchema_, outputParameterSchema_, prompt_)
    
    def run():
        pass