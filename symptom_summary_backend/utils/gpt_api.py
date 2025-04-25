import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarise_entries(entries: list[str]) -> str:
    prompt_text = "\n\n".join(entries)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a health-aware assistant summarising symptom logs."},
            {"role": "user", "content": f"Summarise the following symptom entries from the past week:\n\n{prompt_text}"}
        ],
        temperature=0.3
    )

    summary = response.choices[0].message.content
    return summary
