import os
import openai

###########################
## Configuration Options ##
###########################

CHOSEN_COMP_MODEL = os.environ.get("CHOSEN_COMP_MODEL", "gpt-4-128k")
MAX_OUTPUT_TOKENS = int(os.environ.get("MAX_OUTPUT_TOKENS", "750"))

########################
## Endpoints and Keys ##
########################

COG_SERV_ENDPOINT = os.environ.get("COG_SERV_ENDPOINT", "")
COG_SERV_KEY = os.environ.get("COG_SERV_KEY", "")

OPENAI_RESOURCE_ENDPOINT = os.environ.get("OPENAI_RESOURCE_ENDPOINT", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

###################
## OpenAI Params ##
###################

OPENAI_API_VERSION = os.environ.get("OPENAI_API_VERSION", "2023-03-15-preview")
openai.api_type = "azure"
openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_RESOURCE_ENDPOINT
openai.api_version = OPENAI_API_VERSION

############################
## Defaults and Constants ##
############################

GPT35_TURBO_COMPLETIONS_MODEL = os.environ.get("GPT35_TURBO_COMPLETIONS_MODEL", "gpt-35-turbo")
GPT35_TURBO_COMPLETIONS_MAX_TOKENS = int(os.environ.get("GPT35_TURBO_COMPLETIONS_MAX_TOKENS", "8193"))
GPT35_TURBO_COMPLETIONS_ENCODING = os.environ.get("GPT35_TURBO_COMPLETIONS_ENCODING", "cl100k_base")

GPT4_COMPLETIONS_MODEL_MAX_TOKENS =  int(os.environ.get("GPT4_COMPLETIONS_MODEL_MAX_TOKENS", "8192"))
GPT4_32K_COMPLETIONS_MODEL_MAX_TOKENS = int(os.environ.get("GPT4_32K_COMPLETIONS_MODEL_MAX_TOKENS", "32768"))
GPT4_MODEL = os.environ.get("GPT4_MODEL", "gpt-4")
GPT4_32K_MODEL = os.environ.get("GPT4_32K_MODEL", "gpt-4-32k")
GPT4_128K_MODEL = os.environ.get("GPT4_128K_MODEL", "gpt-4-128k")
GPT4_128K_COMPLETIONS_MODEL_MAX_TOKENS = int(os.environ.get("GPT4_128K_COMPLETIONS_MODEL_MAX_TOKENS", "131072"))