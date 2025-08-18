import json
import os

#AI prompted script to extract text from the json 
def extract_text_from_json(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = data.get("analyzeResult", {}).get("content", None)

    if pages:
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write(pages)
        print(f"✅ Extracted full content to {output_path}")
    else:
        # Fallback: use page-level content if full text not available
        print("⚠️ 'content' field not found. Attempting page-wise reconstruction.")
        pages = data.get("analyzeResult", {}).get("pages", [])
        lines = []
        for i, page in enumerate(pages, 1):
            lines.append(f"\n=== Page {i} ===\n")
            for line in page.get("lines", []):
                lines.append(line.get("content", ""))
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write("\n".join(lines))
        print(f"✅ Reconstructed text to {output_path}")

# Example usage
if __name__ == "__main__":
    input_json = "extracted-jsons/layout_result.json"  # Change if needed
    output_txt = "readable_output.txt"
    extract_text_from_json(input_json, output_txt)
