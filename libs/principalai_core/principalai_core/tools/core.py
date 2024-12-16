from pydantic import BaseModel, ValidationError
from typing import Optional, Callable
import requests
from warnings import warn

from principalai_core.invocable.core import Invocable, FunctionInvocable
from principalai_core.data.models.core import Entity
from principalai_core.utils.errors import (
    IncorrectDefinitonError,
    DoesNotExistError,
    HttpRequestError
)
from principalai_core.utils.http import HttpRequestType

class Tool(Invocable):
    """Base class for Tool - Tools allow LLMs to perform actions outside of generation."""
    def __init__(
        self,
        name_: str, 
        description_: Optional[str] = None, 
        inputParameterSchema_: Optional[BaseModel] = None, 
        outputParameterSchema_: Optional[BaseModel] = None
    ):
        super().__init__(inputParameterSchema_, outputParameterSchema_)
        self.attributes: Entity = Entity(name_, description_)

class FunctionTool(Tool, FunctionInvocable):
    """Tools that are implemented as functions."""
    def __init__(
        self,
        name_: str, 
        description_: Optional[str] = None, 
        inputParameterSchema_: Optional[BaseModel] = None,
        outputParameterSchema_: Optional[BaseModel] = None, 
        func_: Optional[Callable] = None
    ):
        super().__init__(name_, description_, inputParameterSchema_, outputParameterSchema_)
        self.func = func_

    def __call__(
        self, 
        func_: Callable
    ):
        """Function decorator"""
        self.func = func_
        if self.attributes.description is None:
            funcDocstring = func_.__doc__
            if funcDocstring is None:
                raise IncorrectDefinitonError('''Function is missing Docstring. Please add a docstring to the function or 
                                              initialize the tool without a decorator.''')
            self.attributes.description = funcDocstring
        else:
            #Not really required but good to let the user know
            if func_.__doc__ is not None:
                warn('''Function Tool description provided as parameter and in function docstring. The parameter takes 
                     precedence over the function docstring. In case both are same, you can safely remove the description 
                     parameter.''')
        return self
    
    def run(
        self,
        *args,
        **kwargs
    ):
        if not self.func:
            raise DoesNotExistError('''Function does not exist in Function Tool. Please check your code again to make sure that 
                                    you're passing in a callable function during initialization.''')
        runOutput = None
        if self.inputParameterSchema is None:
            try:
                runOutput = self.func(*args, **kwargs)
            except TypeError:
                raise TypeError(f'Tool {self.name} was expecting no parameters. Please check the input schema provided and the function parameters.')
            
        else:
            if self.inputParameterSchema is None:
                warn('''Input parameter schema does not exist. To invoke a Function Tool with paramters, a pydantic 
                     BaseModel schema or Entity list needs to be provided for input paramters.''')
            try:
                runOutput = self.func(*args, **kwargs)
            except TypeError as e:
                raise TypeError(f'Tool {self.name} was called with incorrect paramters: {e}.\nPlease check the input schema provided and the function parameters.')
        return runOutput

class ApiTool(Tool):
    """Tools that are implemented as API Endpoints. When these tools are invoked, the API endpoint should be called."""
    def __init__(
        self,
        name_: str, 
        description_: Optional[str] = None,
        apiEndpoint_: Optional[str] = None,
        httpRequestType_: Optional[HttpRequestType] = HttpRequestType.GET.name.lower(),
        httpParameters_: dict = {}, #Dictionary to provide HTTP request parameters except for inputs
        inputParameterSchema_: Optional[BaseModel] = None,
        outputParameterSchema_: Optional[BaseModel] = None,
        inputParameterParser_: Optional[Callable] = None #Custom parser. Can be used to put data into Url Paramter, Body, etc.
    ):
        super().__init__(name_, description_, inputParameterSchema_, outputParameterSchema_)
        self.func = None
        self.apiEndpoint = apiEndpoint_
        self.httpRequestType = httpRequestType_
        self.httpParameters = httpParameters_
        if inputParameterParser_ is None:
            self.inputParameterParser = self.inputParameterParserFunc
        else:
            self.inputParameterParser = inputParameterParser_
    
    def __call__(
        self,
        func_: Callable
    ):
        """
        Function decorator
        Allows for passing in ApiTool specific variables through the function body.

        @ApiTool
        def api_tool_function():
            return {
                "apiEndpoint_": "https://host.com:port/someendpoint"
            }
        """
        self.func = func_    
        if self.attributes.description is None:
            funcDocstring = func_.__doc__
            if funcDocstring is None:
                raise IncorrectDefinitonError('''Function is missing Docstring. Please add a docstring to the function or 
                                              initialize the tool without a decorator.''')
            self.attributes.description = funcDocstring
        else:
            #Not really required but good to let the user know
            if func_.__doc__ is not None:
                warn('''Function Tool description provided as parameter and in function docstring. The parameter takes 
                     precedence over the function docstring. In case both are same, you can safely remove the description 
                     parameter.''')
        return self

    def run(
        self,
        *args,
        **kwargs
    ):
        #Run the function to get required variables
        functionVariables = self.func()   
        if self.apiEndpoint is None:
            if "apiEndpoint_" in functionVariables:
                self.apiEndpoint = functionVariables["apiEndpoint_"]
            else:
                raise IncorrectDefinitonError(f'''apiEndpoint is not provided in either the function or passed in during 
                                              instantiation. Please check the variable name and if it is passed in
                                              correctly.''')
        else:
            #Already populated warning
            pass
        if "httpRequestType_" in functionVariables:
            if self.httpRequestType is not None:
                ##lready populated warning
                pass
            self.httpRequestType = functionVariables["httpRequestType_"]
        if "httpParameters_" in functionVariables:
            if self.httpRequestType is not None:
                #Already populated warning
                pass
            self.httpParameters = functionVariables["httpParameters_"]

        try:
            requestMethod = getattr(requests, self.httpRequestType)
            if not callable(requestMethod):
                raise HttpRequestError(f'Invalid HTTP request method: {self.httpRequestType}')
            inputParametersParsed = self.inputParameterParser(*args, **kwargs)
            response = requestMethod(self.apiEndpoint, **inputParametersParsed, **self.httpParameters)
            if self.outputParameterSchema is None:
                return response.json()
            else:
                try:
                    validatedOutput = self.outputParameterSchema[0](response.json())
                except ValidationError as e:
                    raise ValidationError(f'''Tool {self.name} could not validate the API response. Please check the output
                                          parameter schema passed in and the API response.: {e}''')
                return validatedOutput
        except requests.RequestException as e:
            raise HttpRequestError(f'Http request failed: {e}')
    
    def inputParameterParserFunc(
        self,
        *args,
        **kwargs
    ):
        """Default parser for HTTP Requests. Since the default type is GET, the data gets places in params"""
        return {
            "params": (self.inputParameterSchema[0](*args, **kwargs)).model_dump()
        }