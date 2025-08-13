import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

#Load API key and endpoint
api_key = os.getenv("API_KEY")
endpoint = os.getenv("ENDPOINT").rstrip("/")

#SAS URL form blob storage
pdf_url = os.getenv("PDF_SAS_URL")

headers = {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": api_key
}

#Submit the analysis request
analyze_url = f"{endpoint}/formrecognizer/documentModels/prebuilt-layout:analyze?api-version=2023-07-31"
payload = {
    "urlSource": pdf_url
}

#Submit request to API
print("Submitting request to Document Intelligence API...")
response = requests.post(analyze_url, headers=headers, json=payload)

print("Status code:", response.status_code)
print("Error response:", response.text)

response.raise_for_status()

operation_url = response.headers["Operation-Location"]
print(f"Operation URL: {operation_url}")

#Poll the operation result
print("Waiting for analysis to complete...")
while True:
    result_response = requests.get(operation_url, headers=headers)
    result_json = result_response.json()
    status = result_json.get("status")

    if status == "succeeded":
        print("Analysis complete!")
        break
    elif status == "failed":
        print("Analysis failed.")
        print(result_json)
        exit()
    
    time.sleep(2)

# Save output to JSON
output_file = "layout_result.json"
with open(output_file, "w", encoding="utf-8") as f:
    import json
    json.dump(result_json, f, indent=2)

print(f"Output saved to: {output_file}")