import pandas as pd
import numpy as np

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, FormRecognizerApiVersion


from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

from utils.env_vars import *


document_analysis_client = DocumentAnalysisClient(COG_SERV_ENDPOINT, AzureKeyCredential(COG_SERV_KEY), api_version="2023-07-31")

def fr_analyze_doc(url):

    poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", url)
    result = poller.result()

    contents = ''

    for paragraph in result.paragraphs:
        contents += paragraph.content + '\n'

    
    for kv_pair in result.key_value_pairs:
        key = kv_pair.key.content if kv_pair.key else ''
        value = kv_pair.value.content if kv_pair.value else ''
        kv_pairs_str = f"{key} : {value}"
        contents += kv_pairs_str + '\n'

    for table_idx, table in enumerate(result.tables):
        row = 0
        row_str = ''
        row_str_arr = []

        for cell in table.cells:
            if cell.row_index == row:
                row_str += ' | ' + str(cell.content)
            else:
                row_str_arr.append(row_str)
                row_str = ''
                row = cell.row_index
                row_str += ' | ' + str(cell.content)

        row_str_arr.append(row_str)
        contents += '\n'.join(row_str_arr) +'\n'

    return contents

@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(10))
def fr_analyze_local_doc_with_dfs(path, verbose = True):

    with open(path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document("prebuilt-document", document=f)

    result = poller.result()
    
    contents = ''
    kv_contents = ''
    t_contents = ''

    for kv_pair in result.key_value_pairs:
        key = kv_pair.key.content if kv_pair.key else ''
        value = kv_pair.value.content if kv_pair.value else ''
        kv_pairs_str = f"{key} : {value}"
        kv_contents += kv_pairs_str + '\n'

    for paragraph in result.paragraphs:
        contents += paragraph.content + '\n'


    for table_idx, table in enumerate(result.tables):
        row = 0
        row_str = ''
        row_str_arr = []

        for cell in table.cells:
            if cell.row_index == row:
                row_str += ' \t ' + str(cell.content)
            else:
                row_str_arr.append(row_str )
                row_str = ''
                row = cell.row_index
                row_str += ' \t ' + str(cell.content)

        row_str_arr.append(row_str )
        t_contents += '\n'.join(row_str_arr) +'\n\n'  
            
    dfs = []     

    return contents, kv_contents, dfs, t_contents