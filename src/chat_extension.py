import openai
import time
from openai import AzureOpenAI

# Set up your OpenAI API key
openai.api_key = ''

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint='https://sabg-xa-azopenai.openai.azure.com/',
    api_key='',
    api_version="2024-02-01",
)

# AI dialogue
def start_conversation(messages):
    # Send a chat request
    response = client.chat.completions.create(
        model="BeyondCase002",
        messages=messages,
        temperature=0.1,  # Temperature parameter, text diversity, high -> high diversity
        top_p=1,  # nucleus The higher the more accurate
        frequency_penalty=0,  # Repetitive words
        max_tokens=4000,  # Control the maximum length of text you pass in and out
        stop=None  # Stop words
    )
    
    return response.choices[0].message.content.strip()

# # Fine-tuning the model
def fine_tuning():
    # upload data
    response = client.files.create(
        file=open("train.jsonl", 'rb'),
        purpose='fine-tune'
    )
    file_id = response.id
    # Creating a fine-tuning job
    fine_tune_response = client.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-35-turbo-0613",  # Or other basic models
        seed = 105
    )
    fine_tune_id = fine_tune_response.id

    # Monitor the status of fine-tuning jobs
    while True:
        status_response = client.fine_tunes.retrieve(id=fine_tune_id)
        status = status_response['status']
        if status in ['succeeded', 'failed']:
            break
        print(f"Status: {status}")
        time.sleep(60)  # Check every minute

    # Get the fine-tuned model ID
    fine_tuned_model = status_response['fine_tuned_model']

    return fine_tuned_model
