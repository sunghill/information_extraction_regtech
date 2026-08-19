import json
import os
import pickle
import time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env.txt")
client = OpenAI()

SYSTEM_PROMPT = """You are an expert systems engineer specializing in regulatory requirement analysis.
Extract every normative requirement from the provided context.
A requirement is any statement containing obligations, constraints, behaviors,
performance criteria, test criteria, environmental conditions, diagnostics,
or interface expectations.

For each requirement extract:
- id
- clause_ref
- requirement_type
- text
- actor
- action
- object
- conditions
- source_clause

Extraction rules:
1. Preserve the original requirement text verbatim.
2. Identify the responsible entity as 'actor'.
3. Identify the required behavior as 'action'.
4. Identify the target of the action as 'object'.
5. Extract any preconditions, triggers, exceptions, or constraints into 'conditions'.
6. Populate clause_ref and source_clause using the regulation clause number.
7. Generate sequential IDs (1.1, 1.2, 1.3, ...).
8. Classify requirement_type as one of:
   - functional
   - performance
   - test
   - interface
   - diagnostic
   - environmental
   - other
9. If a field cannot be determined, use null.

Output your response strictly as a JSON list of objects containing these keys."""


def get_text_chunks(data, max_chars=12000):
  raw_texts = []
  if isinstance(data, (list, tuple)):
    for item in data:
      raw_texts.append(str(item))
  else:
    raw_texts.append(str(data))

  final_chunks = []
  for text in raw_texts:
    if len(text) <= max_chars:
      final_chunks.append(text)
    else:
      paragraphs = text.split("\n")
      current_chunk = ""
      for p in paragraphs:
        if len(current_chunk) + len(p) < max_chars:
          current_chunk += p + "\n"
        else:
          if current_chunk.strip():
            final_chunks.append(current_chunk)
          current_chunk = p + "\n"
      if current_chunk.strip():
        final_chunks.append(current_chunk)

  return final_chunks


def process_pkl_file(pkl_path, model="gpt-4o"):
  with open(pkl_path, "rb") as f:
    data = pickle.load(f)

  text_chunks = get_text_chunks(data, max_chars=12000)
  all_requirements = []
  global_id_counter = 1

  print(
      f"File split into {len(text_chunks)} safe chunks. Processing"
      " sequentially..."
  )

  for i, chunk in enumerate(text_chunks):
    print(f"-> Processing chunk {i+1}/{len(text_chunks)}...")

    try:
      response = client.chat.completions.create(
          model=model,
          messages=[
              {"role": "system", "content": SYSTEM_PROMPT},
              {
                  "role": "user",
                  "content": "Here is the context to analyze:\n\n" + chunk,
              },
          ],
          response_format={"type": "json_object"},
      )

      content = response.choices[0].message.content

      # Safety check if model response content is empty/None
      if not content:
        print(
            f"   [Warning] Chunk {i+1} returned empty content. Skipping chunk."
        )
        continue

      parsed_data = json.loads(content)

      if isinstance(parsed_data, dict):
        for key, value in parsed_data.items():
          if isinstance(value, list):
            parsed_data = value
            break

      if isinstance(parsed_data, list):
        for req in parsed_data:
          req["id"] = f"1.{global_id_counter}"
          global_id_counter += 1
          all_requirements.append(req)

    except Exception as e:
      print(f"   [Error] Failed processing chunk {i+1}: {e}. Skipping chunk.")

    time.sleep(2)

  return all_requirements


def main():
  pkl_files = ["data/UNR152r2e_chunks.pkl"]  # Update paths as needed

  for pkl_file in pkl_files:
    if not os.path.exists(pkl_file):
      print(f"File not found: {pkl_file}")
      continue

    base_name = os.path.splitext(pkl_file)[0]
    print(f"\n--- Starting {pkl_file} ---")

    requirements = process_pkl_file(pkl_file)

    json_output = f"{base_name}_requirements.json"
    csv_output = f"{base_name}_requirements.csv"

    with open(json_output, "w", encoding="utf-8") as f:
      json.dump(requirements, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame(requirements)
    df.to_csv(csv_output, index=False, encoding="utf-8")

    print(f"Successfully Saved: {json_output} and {csv_output}")


if __name__ == "__main__":
  main()