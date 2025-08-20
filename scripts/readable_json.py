import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_json(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = data.get("analyzeResult", {}).get("content", None)

    if pages:
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write(pages)
        print(f"Extracted full content to {output_path}")
    else:
        print("'content' field not found. Attempting page-wise reconstruction.")
        pages = data.get("analyzeResult", {}).get("pages", [])
        lines = []
        for i, page in enumerate(pages, 1):
            lines.append(f"\n=== Page {i} ===\n")
            for line in page.get("lines", []):
                lines.append(line.get("content", ""))
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write("\n".join(lines))
        print(f"Reconstructed text to {output_path}")

def ask_gpt_for_structured_json(prompt_text: str, extracted_text: str):
    system_message = {
        "role": "system",
        "content": "You are a document parser. Extract structured JSON fields from text according to task instructions."
    }

    user_message = {
        "role": "user",
        "content": f"{prompt_text}\n\nDocument Content:\n{extracted_text}"
    }

    print("Sending content to GPT-4o...")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[system_message, user_message],
        temperature=0.2,
    )

    #Extract content
    result = response.choices[0].message.content

    return result

def save_output(output_json_str, filename="structured_output.json"):
    #Remove '''json if possible
    if output_json_str.startswith("```json"):
        output_json_str = output_json_str.strip().removeprefix("```json").removesuffix("```").strip()

    try:
        data = json.loads(output_json_str)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Structured JSON saved to {filename}")
    except json.JSONDecodeError:
        print("GPT output is not valid JSON. Saving raw text instead.")
        with open("raw_output.txt", "w", encoding="utf-8") as f:
            f.write(output_json_str)

# ==== MAIN ====
if __name__ == "__main__":
    input_json = "extracted-jsons/layout_result.json"
    output_txt = "readable_output.txt"

    #Extract text to file
    extract_text_from_json(input_json, output_txt)

    #Load text for GPT
    with open(output_txt, "r", encoding="utf-8") as f:
        extracted_text = f.read()

    #Custom prompt
    custom_prompt = (
        "You are a data extraction agent. From the following incentive document, "
        "extract a JSON object with the following fields:\n\n"
        "- program_name\n"
        "- technology\n"
        "- region\n"
        "- eligibility_rules\n"
        "- cap_amount\n"
        "- application_deadline\n"
        "- stackability_notes\n"
        "- incentive_type (rebate, credit, etc)\n"
        "- value_per_unit (e.g., $/kWh or $/ton)\n"
        "- admin_agency\n"
        "- relevant_links\n\n"
        "Output a clean JSON object. Do not include commentary."
    )

    #Ask GPT and save response
    gpt_output = ask_gpt_for_structured_json(custom_prompt, extracted_text)
    save_output(gpt_output)
