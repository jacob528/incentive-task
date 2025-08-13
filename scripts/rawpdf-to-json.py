import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

#Load API key and endpoint
api_key = os.getenv("API_KEY")
endpoint = os.getenv("ENDPOINT")

headers = {
    "Ocp-Apim-Subscription-Key": api_key,
    "Content-Type": "application/json"
}

#Get model info
response = requests.get(
    endpoint.rstrip("/") + "/formrecognizer/documentModels/prebuilt-layout?api-version=2023-07-31",
    headers=headers
)

print(response.json())
