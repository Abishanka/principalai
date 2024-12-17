from pydantic import BaseModel
from typing import Optional, Callable
from warnings import warn

from principalai_core.data import Entity
from principalai_core.utils.parsers import entity_parameter_parser
from principalai_core.language_models import LanguageModel
from principalai_core.utils.errors import DoesNotExistError

class Invocable():
    """Unit of a task/work/process that can invoked/run/executed. May use a language model."""
    def __init__(
        self,
        inputParameterSchema: Optional[BaseModel] = None, 
        outputParameterSchema: Optional[BaseModel] = None,
        languageModel: LanguageModel = None,
        languageModelRunEngine: Callable = None
    ):
        '''
        Parameters for input and output can be passed in as pydantic base classes/schemas.
        This does 2 things:
            1. Ensures schema and type strictness
            2. Allows for easy parsing to eventually be used
        '''
        self.inputParameterSchema: Optional[tuple[BaseModel, list[Entity]]] = None
        if type(inputParameterSchema) is BaseModel: 
            self.inputParameterSchema = tuple(inputParameterSchema, entity_parameter_parser(inputParameterSchema))

        self.outputParameterSchema: Optional[tuple[BaseModel, list[Entity]]] = None
        if type(outputParameterSchema) is BaseModel:
            self.outputParameterSchema = tuple(outputParameterSchema, entity_parameter_parser(outputParameterSchema))
        
        self.languageModel: Optional[LanguageModel] = languageModel
        '''
        Language Model Run Engine (LMRE) serves as a pre-configured single entry point to call a language model.

        Why an LMRE:
            1. Since LMRE's are functions, they can be reused across different Invocables.
            2. Helps in abstracting away message creation from the actual LLM call.
            3. LMRE's allow developers fine grained control over all messages
            4. Lastly, LMRE's can be of any type: Completions, Embeddings, Specialized, etc.

        The LMRE serves as the default language model call for an Invocable. There can be multiple "local" LMREs
        depending on the application architecture.
        '''
        self.languageModelRunEngine: Callable = languageModelRunEngine
    
    @property
    def run(self, *args, **kwargs):
        return None
    
    def set_language_model(self, languageModel: LanguageModel) -> None:
        """Set LanguageModel provider"""
        self.languageModel = languageModel
        self.languageModelRunEngine = languageModel.run

    def get_language_model(self) -> LanguageModel:
        return self.languageModel
    
    def set_language_model_run_engine(self, languageModelRunEngine: Callable):
        """Set LanguageModelRunEngine"""
        self.languageModelRunEngine = languageModelRunEngine

class FunctionInvocable(Invocable):
    """Invocables implemented as functions. Allows to implement Invocables through @Decorators"""
    def __init__(
        self,
        inputParameterSchema: Optional[BaseModel] = None, 
        outputParameterSchema: Optional[BaseModel] = None,
        languageModel: LanguageModel = None,
        languageModelRunEngine: Callable = None
    ):
        super().__init__(inputParameterSchema, outputParameterSchema, languageModel, languageModelRunEngine)
        self.func = None
        
    def __call__(
        self,
        func: Callable
    ):
        """Function decorator"""
        self.func = func
        return self
    
    def run(
        self,
        *args,
        **kwargs
    ):
        if not self.func:
            raise DoesNotExistError(f'''Function does not exist in Invocable. Please check your code again to make sure that 
                                    you're passing in a callable function during initialization.''')
        if self.inputParameterSchema is None:
            warn('''Input parameter schema does not exist. To invoke a Function Invocable with paramters, a pydantic 
                     BaseModel schema or Entity list should be provided for input paramters.''')
        runOutput = self.func(*args, **kwargs)
        return runOutput