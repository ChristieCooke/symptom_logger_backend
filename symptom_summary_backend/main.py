import os
import requests
import datetime
from dotenv import load_dotenv
from openai import OpenAI
import json
import utils

#Load environment variables from .env
load_dotenv()

#Get secrets from .env
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
SYMPTOM_DB_ID = os.getenv("NOTION_SYMPTOMLOG_DATABASE_ID")
SUMMARY_DB_ID = os.getenv("NOTION_SUMMARY_DATABASE_ID")
TRIGGER_DB_ID = os.getenv("NOTION_TRIGGER_LOG_DATABASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#Get Helper Functions from utils
from utils.notion_api import (
    get_recent_symptoms,
    get_recent_entries_raw,
    update_entry_titles_conditionally,
    find_summary_page_id,
    update_summary,
)

#Get Helper Functions from utils
from utils.gpt_api import summarise_entries


if __name__ == "__main__":
    # Get the symptom log entries (you’ve already built this)
    raw_text, _ = get_recent_symptoms()  # or however your function is named

    # Generate GPT summary
    summary_text = summarise_entries(raw_text)

    # ✅ Fix: convert list to string if needed
    if isinstance(raw_text, list):
        raw_text = "\n".join(raw_text)

    # Get the summary row from Notion
    page_id = find_summary_page_id(NOTION_API_KEY, SUMMARY_DB_ID, "1 Week Summary")

    # Post the summary + dates back to Notion
    status = update_summary(NOTION_API_KEY, page_id, summary_text, raw_text)

    if status == 200:
        print("✅ Summary successfully updated in Notion.")
    else:
        print(f"❌ Failed to update Notion. Status code: {status}")
