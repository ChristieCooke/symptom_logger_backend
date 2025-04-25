from flask import Flask, request, jsonify
import os
import datetime
from dotenv import load_dotenv

from utils.notion_api import (
    get_recent_symptoms,
    update_entry_titles_conditionally,
    find_summary_page_id,
    update_summary,
    update_trigger_status,
    update_summary_date
)

from utils.gpt_api import summarise_entries

# Load environment variables
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
SUMMARY_DB_ID = os.getenv("NOTION_SUMMARY_DATABASE_ID")

# Create a Flask app instance (this is your web server)
app = Flask(__name__)

# Define a route that runs when someone POSTs to /run-summary
@app.route("/run-summary", methods=["POST"])
def run_summary():
    try:
        # Debug: Confirm webhook is reaching Flask
        print("Webhook hit!")
        data = request.json


        # Get Trigger Log row ID from webhook payload
        trigger_page_id = data["data"]["id"]
        print(f"Trigger Log page ID: {trigger_page_id}")

        # Get Trigger Log title (e.g. "1 Week Trigger" or "4 Week Trigger")
        try:
            trigger_title = data["data"]["properties"]["Name"]["title"][0]["text"]["content"]
            print(f"Triggered by row: {trigger_title}")
        except (KeyError, IndexError) as e:
            print("Could not extract trigger title:", e)
            trigger_title = "Unknown"
        if "4" in trigger_title:
            duration_days = 28
        else:
            duration_days = 7
        print(f"Duration set to: {duration_days} days")
    

        # Get Trigger Log row ID from webhook payload
        trigger_page_id = data["data"]["id"]
        print(f"Trigger Log page ID: {trigger_page_id}")

        # Step 1: Update status to Running
        update_trigger_status(trigger_page_id, "Running")
        print("Status updated to 'Running'")

        # Step 2: Pull recent symptoms
        formatted_text, raw_entries = get_recent_symptoms(duration_days)
        update_entry_titles_conditionally(NOTION_API_KEY, raw_entries)


        if not formatted_text:
            update_trigger_status(trigger_page_id, "❌ Error")
            return jsonify({"message": "No symptom entries found."}), 200

        # Step 3: Generate GPT summary
        summary = summarise_entries(formatted_text)

        # Step 4: Clean up raw text if needed
        if isinstance(formatted_text, list):
            formatted_text = "\n".join(formatted_text)

        # Step 5: Find the Notion summary page (1-week for now)
        summary_page_id = find_summary_page_id(NOTION_API_KEY, SUMMARY_DB_ID, "1 Week Summary")

        # Step 6: Post the summary + raw text
        status = update_summary(NOTION_API_KEY, summary_page_id, summary, formatted_text)

        # Step 7: Final status update
        if status == 200:
            update_trigger_status(trigger_page_id, "✅ Done")
            update_summary_date(trigger_page_id)
            return jsonify({"message": "Summary posted to Notion."}), 200
        else:
            update_trigger_status(trigger_page_id, "❌ Error")
            return jsonify({"error": f"Notion update failed with status {status}"}), 500

    except Exception as e:
        print("Error during webhook:", e)
        try:
            update_trigger_status(trigger_page_id, "❌ Error")
        except:
            print("Failed to update error status")
        return jsonify({"error": str(e)}), 500


# Run the app on your machine (http://localhost:5000)
if __name__ == "__main__":
    app.run(debug=True, port=5000)
