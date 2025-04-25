Symptom Summary System — Python Backend

A lightweight Flask backend that integrates with Notion and OpenAI GPT-4 to automatically summarize symptom log entries and post the results back to your Notion workspace.

This backend powers the Tier 3 (Python automation) version of the Symptom Summary System.

✨ Features


Automatically fetches recent symptom entries from your Notion Symptom Log.

Summarizes symptoms into a clean, professional report using GPT-4.

Posts the summary and raw log back into Notion.

Supports different summary durations (e.g., 1-week, 4-week).

Modular and ready for future deployment or scaling.


📦 Project Structure


symptom-summary-backend/
│
├── app.py                  # Main Flask app
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables file
├── README.md                # Setup and usage instructions
│
├── utils/                   # (Optional) Helper modules (if created)
│
└── .gitignore               # Ignore secrets and cache files


🚀 Quick Start (Experienced Users)


git clone https://github.com/yourusername/symptom-summary-backend.git
cd symptom-summary-backend
pip install -r requirements.txt
cp .env.example .env    # Create your own .env file with real credentials
python app.py

Use ngrok to expose your Flask server:

ngrok http 5000

Then connect your Notion Automation webhook to:

https://your-ngrok-url.com/run_summary


🧠 Full Setup Guide

## OPTIONAL ---📦 Make.com Automation Version (Tier 2)

For users who prefer no local Python setup, a full Make.com automation is available.

- Import the JSON file found in the `/make/` folder.
- Set up your environment variables and Notion connections inside Make.
- The automation runs fully in the cloud (paid Make plan recommended for production use).

✅ No Python server required.



ALTERNATIVE FULL PYTHON BACKEND:::


1. Prerequisites
Python 3.10 or newer installed

ngrok account installed

OpenAI API Key (from OpenAI)

Notion Integration with database access (Guide)

Notion API Key - Sourced ithin Notion, Profile - Settings - Connections - Develop or manage integrations - Create Integration
Notion Database ID - Sourced On relevant database - click the three dots in the top right of the DB - select copy link - extract the ID from between the final "/" and the "?"
OpenAI API Key - Sourced within Open AI profile settings

2. Install Dependencies
In your project folder:

pip install -r requirements.txt

3. Set Up Environment Variables
Create a .env file based on the .env.example provided.

Required fields:

NOTION_API_KEY=your_notion_secret_key
OPENAI_API_KEY=your_openai_key
NOTION_TRIGGER_DATABASE_ID=your_trigger_log_database_id
NOTION_SYMPTOM_DATABASE_ID=your_symptom_log_database_id
4. Run the Flask App Locally
python app.py
This will start your local webhook server at http://localhost:5000.

5. Expose Your Server to the Internet
Start ngrok in a separate terminal:

ngrok http 5000
Copy your ngrok URL (e.g., https://abcd1234.ngrok.io).

6. Connect Notion Automations
Create a Notion Automation.

Set the trigger (e.g., a checkbox ticked or a trigger row created).

Action: Send a POST webhook to:

https://your-ngrok-url.com/run_summary


7. Using the System
Open your Symptom Logger.

Press the Trigger Summary button.

Your backend will:

Fetch symptoms from the past week or month.

Summarize them with GPT-4.

Post the results back into Notion.

🎉 Done!


🔥 Credits
Built by [Christie Cooke]
Part of the Symptom Summary System suite.

📈 System Flow Diagram
[User clicks Button in Notion]
            ↓
[Notion Automation triggers Webhook]
            ↓
[Webhook received by Flask App (via ngrok URL)]
            ↓
[Flask App fetches Symptom Log entries from Notion]
            ↓
[Flask App formats prompt and calls OpenAI API (GPT-4)]
            ↓
[OpenAI returns Symptom Summary]
            ↓
[Flask App posts Summary + Raw Log back into Notion]
            ↓
[User views updated Symptom Summary in Notion]
🧹 Notes
Keep your .env file private.

If testing multiple users or databases, update your database IDs accordingly.

API usage charges may apply (OpenAI, ngrok Pro if you upgrade).

📬 Contact
For questions, improvements, or collaboration, reach out at [Bongocity on Github or christiecooke@hotmail.com].