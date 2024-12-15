from pydantic import BaseModel
from typing import Optional, Callable
import requests
from warnings import warn

from principalai_core.data.models.core import Entity
from principalai_core.utils.errors import IncorrectDefinitonError, DoesNotExistError, HttpRequestError
from principalai_core.data.parsers.core import entity_parameter_parser
from principalai_core.utils.http import HttpRequestType

class Tool(BaseModel):
    """Base class for Tool - Tools allow LLMs to perform actions outside of generation."""
    def __init__(
        self, 
        name_: str, 
        description_: str | None=None, 
        inputParameters_: BaseModel | None=None, 
        outputParameters_: BaseModel | None=None
    ):
        self.name: str =  name_
        self.description: str = description_
        '''
        Parameters for input and output are passed in as pydantic base classes/schemas.
        This does 2 things:
            1. Ensures schema and type strictness
            2. Allows for easy parsing to eventually be used
        '''
        self.inputParameters: list[Entity] | None = entity_parameter_parser(inputParameters_)
        self.outputParameters: list[Entity] | None = entity_parameter_parser(outputParameters_)
    
    @property
    def run():
        """Invoke the tool. To be implemented in child classes"""
        return None

class FunctionTool(Tool):
    """Function tools are Tools that are developed as functions."""
    def __init__(
        self,
        name_: str, 
        description_: str | None=None, 
        inputParameters_: BaseModel | None=None, 
        outputParameters_: BaseModel | None=None,
        func_: Callable | None = None
    ):
        super(name_, description_, inputParameters_, outputParameters_).__init__()
        self.func = func_

    def __call__(
        self, 
        func_: Callable
    ):
        """Function decorator"""
        self.func = func_
        if self.description is None:
            funcDocstring = func_.__doc__
            if funcDocstring is None:
                raise IncorrectDefinitonError('''Function is missing Docstring. Please add a docstring to the function or 
                                              initialize the tool without a decorator.''')
            self.description = funcDocstring
        else:
            #Not really required but good to let the user know
            if func_.__doc__ is not None:
                warn('''Function Tool description provided as parameter and in function docstring. The parameter takes 
                     precedence over the function docstring. In case both are same, you can safely remove the description 
                     parameter.''')
        return self
    
    def run(self, inputParameters_: BaseModel | None):
        if not self.func:
            raise DoesNotExistError('''Function does not exist in Function Tool. Please check your code again to make sure that 
                                    you're passing in a callable function during initialization.''')
        runOutput = None
        if inputParameters_ is None:
            runOutput = self.func()
        else:
            if self.inputParameters is None:
                raise DoesNotExistError('''Input parameters schema does not exist. To invoke a Function Tool with paramters, a 
                                        pydantic BaseModel schema or Entity list needs to be provided for input paramters.''')
            validatedInput = self.inputParameters(**inputParameters_)
            runOutput = self.func(**validatedInput.dict())
        
        if self.outputParameters is None:
            return runOutput
        else:
            runOutputValidated = self.outputParameters(runOutputValidated)
            return runOutputValidated

class ApiTool(Tool):
    """API tools are tools developed as API Endpoints. When these tools are invoked, the API endpoint should be called."""
    def __init__(
        self,
        name_: str, 
        description_: str,
        apiEndpoint_: str,
        httpRequestType_: Optional[HttpRequestType] = HttpRequestType.GET.name.lower(),
        httpParameters_: dict = {}, #Dictionary to provide HTTP request parameters except for inputs
        inputParameters_: BaseModel | None = None,
        outputParameters_: BaseModel | None = None,
        inputParameterParser_: Callable | None = None #Custom parser. Can be used to put data into Url Paramter, Body, etc.
    ):
        super(name_, description_, inputParameters_, outputParameters_).__init__()
        self.apiEndpoint = apiEndpoint_
        self.httpRequestType = httpRequestType_
        self.httpParameters = httpParameters_
        if inputParameterParser_ is None:
            self.inputParameterParser = self.inputParameterParserFunc
        else:
            self.inputParameterParser = inputParameterParser_
        
    def run(self, inputParameters_: BaseModel):
        try:
            requestMethod = getattr(requests, self.httpRequestType)
            if not callable(requestMethod):
                raise HttpRequestError(f'Invalid HTTP request method: {self.httpRequestType}')
            inputParametersParsed = self.inputParameterParser(inputParameters_)
            response = requestMethod(self.apiEndpoint, **inputParametersParsed, **self.httpParameters)
            if self.outputParameters is None:
                return response.json()
            else:
                validatedOutput = self.outputParameters(response.json())
                return validatedOutput
        except requests.RequestException as e:
            raise HttpRequestError(f'Http request failed: {e}')
    
    def inputParameterParserFunc(inputParameters_: BaseModel):
        """Default parser for HTTP Requests. Since the default type is GET, the data gets places in params"""
        return {
            "params": inputParameters_.model_dump()
        }