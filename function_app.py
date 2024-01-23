import azure.functions as func
import logging
import json
import time
import os
from azure.storage.blob import BlobServiceClient
from utils import summarization

blob_storage_connection_string = os.getenv('AzureWebJobsStorage')  # Or your custom environment variable for the connection string
blob_container_name = os.getenv('BLOB_CONTAINER_NAME', 'output')  # Provide a default value if not set

blob_service_client = BlobServiceClient.from_connection_string(blob_storage_connection_string)

app = func.FunctionApp()

@app.service_bus_queue_trigger(arg_name="azservicebus", queue_name="inbox", connection="sbconnstring")
def servicebus_queue_trigger(azservicebus: func.ServiceBusMessage):
    # Parse the Service Bus message, which is expected to be a JSON string
    message_body = azservicebus.get_body().decode('utf-8')
    logging.info('Python ServiceBus Queue trigger processed a message: %s', message_body)
    
    # Deserialize the message body to a Python dictionary
    message = json.loads(message_body)
    email = message.get('email')
    file_sas_url = message.get('file_sas_url')
    attachment_name = message.get('attachment_name')

    # Perform the summarization using your existing logic
    if email and file_sas_url:
        summary_result = summarization.summarize_document(file_sas_url, mode='refine', verbose = True)
        summary = summary_result.get('summary')

        # Create a new JSON object with the original content plus the summary
        output_data = {
            "email": email,
            "attachment_name": attachment_name,
            "file_sas_url": file_sas_url,
            "summary": summary
        }

        # Serialize the output data to a JSON string
        output_data_str = json.dumps(output_data)
        
        # Create a unique blob name, for example using the email and a timestamp
        blob_name = f"{email}_{int(time.time())}.json"

        # Get a blob client for the container and blob we want to create
        blob_client = blob_service_client.get_container_client(blob_container_name).get_blob_client(blob_name)

        # Upload the JSON string as a blob
        blob_client.upload_blob(output_data_str, blob_type="BlockBlob")

        logging.info(f"Summary for {email} uploaded to blob storage.")
    else:
        logging.error("The message is missing required information.")
