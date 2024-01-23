import os
import pickle
import numpy as np
import pandas as pd
import urllib
from datetime import datetime, timedelta
import logging
import copy
import uuid
import json
import openpyxl
import time

from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import TokenTextSplitter, TextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.callbacks.base import CallbackManager

from utils import openai_helpers
from utils import helpers

from utils.env_vars import *

mapreduce_prompt_template = """The maximum output is about 500 to 750 tokens, so make sure to take advantage of this to the maximum.\n
Write an elaborate summary of 3 paragraphs of the following:

{text}

SUMMARY:"""


refine_prompt_template = """Write an elaborate summary of 3 paragraphs of the following:

{text}

"""

refine_template = (
    "Your job is to produce a final summary of 3 paragraphs that is elaborate and rich in details.\n" 
    "The maximum output is about 500 to 750 tokens, so make sure to take advantage of this to the maximum.\n"
    "We have provided an existing summary up to a certain point: {existing_answer}\n"
    "We have the opportunity to refine the existing summary."
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{text}\n"
    "------------\n"
    "Given the new context, refine the original summary."
    "If the context isn't useful, return the original summary."
)

def chunk_doc(all_text, mode='refine', model=CHOSEN_COMP_MODEL, max_output_tokens=MAX_OUTPUT_TOKENS, chunk_overlap=500):

    enc_name = openai_helpers.get_encoding_name(model)
    enc = openai_helpers.get_encoder(model)

    max_tokens = openai_helpers.get_model_max_tokens(model)

    if mode == 'refine':
        max_tokens = max_tokens - len(enc.encode(refine_prompt_template)) - len(enc.encode(refine_template)) - 2*MAX_OUTPUT_TOKENS - chunk_overlap
    elif mode == 'map_reduce':
        max_tokens = max_tokens - len(enc.encode(mapreduce_prompt_template)) - MAX_OUTPUT_TOKENS - chunk_overlap
    else:
        raise Exception('Invalid mode')

    text_splitter = TokenTextSplitter(encoding_name=enc_name, chunk_size = max_tokens, chunk_overlap=chunk_overlap)
    
    texts = text_splitter.split_text(all_text)
    docs = [Document(page_content=t) for t in texts]

    enc = openai_helpers.get_encoder(CHOSEN_COMP_MODEL)

    l_arr = []
    for d in texts:
        l_arr.append(str(len(enc.encode(d))))

    print("Chunks Generated", len(docs), ' | max_tokens', max_tokens, " | Chunk Lengths:", ', '.join(l_arr))

    return docs

def clean_up_text(text):
    text = text.replace('....', '')
    return text

def get_refined_summarization(docs, model=CHOSEN_COMP_MODEL, max_output_tokens=MAX_OUTPUT_TOKENS, stream=False, callbacks=[]):
    PROMPT = PromptTemplate(template=refine_prompt_template, input_variables=["text"])
    refine_prompt = PromptTemplate(input_variables=["existing_answer", "text"],template=refine_template)

    llm = helpers.get_llm(model, temperature=0, max_output_tokens=max_output_tokens, stream=stream, callbacks=callbacks)

    chain = load_summarize_chain(llm, chain_type="refine",  question_prompt=PROMPT, refine_prompt=refine_prompt, return_intermediate_steps=True)
    summ = chain({"input_documents": docs}, return_only_outputs=True)
    
    return summ


def get_mapreduced_summarization(docs, model=CHOSEN_COMP_MODEL, max_output_tokens=MAX_OUTPUT_TOKENS, stream=False, callbacks=[]):
    PROMPT = PromptTemplate(template=mapreduce_prompt_template, input_variables=["text"])
    llm = helpers.get_llm(model, temperature=0, max_output_tokens=max_output_tokens, stream=stream, callbacks=callbacks)
    chain = load_summarize_chain(llm, chain_type="map_reduce", map_prompt=PROMPT, combine_prompt=PROMPT, return_intermediate_steps=True)
    summ = chain({"input_documents": docs}, return_only_outputs=True)
    return summ

def summarize_document(text, mode='refine', verbose = False):
    print(f"##########################\nStarting Processing ...")
    start = time.time()

    if text is None: return None

    summ = summarize_text(text, mode=mode, verbose=verbose)
    end = time.time()

    summary = {
        'intermediate_steps': summ['intermediate_steps'],
        'summary': summ['output_text'],
        'proc_time': end-start
    }

    print(f"Done Processing in {end-start} seconds\n##########################\n")
    return summary 

def summarize_text(text, mode='refine', verbose = False):    
    docs = chunk_doc(text, mode=mode)

    if mode == 'refine':
        summ = get_refined_summarization(docs)
    elif mode == 'map_reduce':
        summ = get_mapreduced_summarization(docs)
    else:
        raise Exception("Invalid mode")

    return summ