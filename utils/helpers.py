from langchain.llms import AzureOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager

from utils import openai_helpers

from utils.env_vars import *

def get_llm(model = CHOSEN_COMP_MODEL, temperature=0, max_output_tokens=MAX_OUTPUT_TOKENS, stream=False, callbacks=[]):
    gen = openai_helpers.get_generation(model)

    if (gen == 3) :
        llm = AzureOpenAI(deployment_name=model, model_name=model, temperature=temperature, 
                        openai_api_key=openai.api_key, max_retries=30, 
                        request_timeout=120, streaming=stream,
                        callback_manager=CallbackManager(callbacks),
                        max_tokens=max_output_tokens, verbose = True)
                        
    elif (gen == 4) or (gen == 3.5):
        llm = ChatOpenAI(model_name=model, model=model, engine=model, 
                            temperature=0, openai_api_key=openai.api_key, max_retries=30, streaming=stream,
                            callback_manager=CallbackManager(callbacks),
                            request_timeout=120, max_tokens=max_output_tokens, verbose = True)    
    else:
        assert False, f"Generation unknown for model {model}"                                

    return llm                                  