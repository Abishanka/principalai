from pydantic import BaseModel
from typing import Optional, Callable

from principalai_core.data.models.core import Entity
from principalai_core.data.parsers.core import entity_parameter_parser
from principalai_core.languageModel.core import LanguageModel

class Invocable(BaseModel):
    """Smallest possible unit of a task/work/process that can invoked/run/executed. Can use a language model."""
    def __init__(
        self,
        inputParameterSchema_: Optional[BaseModel] = None, 
        outputParameterSchema_: Optional[BaseModel] = None,
    ):
        '''
        Parameters for input and output can be passed in as pydantic base classes/schemas.
        This does 2 things:
            1. Ensures schema and type strictness
            2. Allows for easy parsing to eventually be used
        '''
        self.inputParameterSchema: Optional[tuple[BaseModel, list[Entity]]] = None
        if type(inputParameterSchema_) is BaseModel: 
            self.inputParameterSchema = tuple(inputParameterSchema_, entity_parameter_parser(inputParameterSchema_))

        self.outputParameterSchema: Optional[tuple[BaseModel, list[Entity]]] = None
        if type(outputParameterSchema_) is BaseModel:
            self.outputParameterSchema = tuple(outputParameterSchema_, entity_parameter_parser(outputParameterSchema_))
        
        self.languageModel: Optional[LanguageModel] = None
    
    @property
    def run():
        return None
    
    def set_language_model(self, languageModel_: LanguageModel) -> None:
        self.languageModel = languageModel_

    def get_language_model(self) -> LanguageModel:
        return self.languageModel

class FunctionInvocable(Invocable):
    """Invocables implemented as functions"""
    def __call__(
        self,
        func_: Callable
    ):
        self.func = func_
        return self
    
    @property
    def run():
        return None