import datetime
import requests
import os

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
SYMPTOM_DB_ID = os.getenv("NOTION_SYMPTOMLOG_DATABASE_ID")



#Auto update "Name" field if set to New Entry
def update_entry_titles_conditionally(notion_api_key, entries):
    """
    Update the Name/title of symptom entries *only* if the current title is still "New Entry"
    """

    for entry in entries:
        page_id = entry["id"]
        properties = entry.get("properties", {})
        title_obj = properties.get("Name", {}).get("title", [])

        current_title = title_obj[0]["text"]["content"] if title_obj else ""
        if current_title == "New Entry":
            # Compose a title using date and symptom fields
            date_str = properties.get("Date", {}).get("date", {}).get("start", "")
            symptom_text = ", ".join([t["name"] for t in properties.get("Symptom", {}).get("multi_select", [])])
            try:
                parsed_date = datetime.datetime.fromisoformat(date_str)
                pretty_date = parsed_date.strftime("%b %d, %H:%M")  # e.g. Apr 23, 08:49
            except Exception:
                pretty_date = date_str  # fallback
            new_title = f"{pretty_date} - {symptom_text}" if pretty_date and symptom_text else pretty_date or "Symptom Entry"    

            # Update the title via PATCH
            url = f"https://api.notion.com/v1/pages/{page_id}"
            headers = {
                "Authorization": f"Bearer {notion_api_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            payload = {
                "properties": {
                    "Name": {
                        "title": [{
                            "text": {"content": new_title}
                        }]
                    }
                }
            }
            response = requests.patch(url, headers=headers, json=payload)
            if not response.ok:
                print(f"Failed to rename entry {page_id}: {response.text}")


#Find GPT export DB page ID (e.g. four week summary etc)
def find_summary_page_id(NOTION_API_KEY, SUMMARY_DB_ID, summary_name):
    url = f"https://api.notion.com/v1/databases/{SUMMARY_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    body = {
        "filter": {
            "property": "Name",
            "title": {
                "equals": summary_name
            }
        }
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    if data["results"]:
        return data["results"][0]["id"]
    else:
        raise Exception("Page not found.")



#Source raw text for time period
def get_recent_symptoms(duration_days=7):
    now = datetime.datetime.now(datetime.UTC)
    start_time = now - datetime.timedelta(days=duration_days)



    # Step 2: Set up Notion API request
    url = f"https://api.notion.com/v1/databases/{SYMPTOM_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # ✅ Step 3: Filter using your "Date" property, not created_time
    payload = {
        "filter": {
            "property": "Date",
            "date": {
                "on_or_after": start_time.isoformat()
            }
        }
    }
    print(f"Fetching entries from: {start_time.isoformat()}")

    # Step 4: Send the request
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    results = response.json()["results"]

    raw_entries = results #save the original notion entries
    # Step 5: Format each result
    formatted_entries = []
    for result in results:
        props = result["properties"]

        date = props.get("Date", {}).get("date", {}).get("start", "No date")
        severity = props.get("Severity", {}).get("number", "N/A")
        symptoms = props.get("Symptom", {}).get("multi_select", [])
        symptom_text = ", ".join([s.get("name", "") for s in symptoms]) if symptoms else "Unspecified"
        notes_blocks = props.get("Notes", {}).get("rich_text", [])
        notes = "".join([block.get("plain_text", "") for block in notes_blocks]) if notes_blocks else "No notes"

        entry_text = f"{date} | Severity: {severity} | Symptom: {symptom_text}\n{notes}"
        formatted_entries.append(entry_text)

    return formatted_entries, raw_entries

#get recent entries for names
def get_recent_entries_raw(duration_days=7):
    now = datetime.datetime.now(datetime.UTC)
    start_time = now - datetime.timedelta(days=duration_days)

    url = f"https://api.notion.com/v1/databases/{SYMPTOM_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    payload = {
        "filter": {
            "property": "Date",
            "date": {
                "on_or_after": start_time.isoformat()
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["results"]


#Paste function
def update_summary(NOTION_API_KEY, page_id, summary_text, raw_text):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    today = datetime.datetime.now().date()
    seven_days_ago = today - datetime.timedelta(days=7)

    body = {
        "properties": {
            "GPT Summary": {
                "rich_text": [
                    {
                        "text": {
                            "content": summary_text
                        }
                    }
                ]
            },
            "Raw Log": {
                "rich_text": [
                    {
                        "text": {
                            "content": chunk

                        }
                    } for chunk in [raw_text[i:i+2000] for i in range(0, len(raw_text), 2000)]
                ]
            },
            "Start Date": {
                "date": {
                    "start": seven_days_ago.isoformat()
                }
            },
            "End Date": {
                "date": {
                    "start": today.isoformat()
                }
            }
        }
    }

    response = requests.patch(url, headers=headers, json=body)
    if response.status_code != 200:
        print("❌ Notion API error response:")
        print(response.text)
    return response.status_code


def update_trigger_status(page_id: str, status: str):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "properties": {
            "Status": {
                "select": {"name": status}
            }
        }
    }

    response = requests.patch(url, headers=headers, json=payload)
    if not response.ok:
        print(f"Failed to update status to '{status}' — {response.text}")

#Helper function to update the date last summarised
def update_summary_date(page_id: str):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "properties": {
            "Date Last Summarised": {
                "date": {
                    "start": datetime.datetime.utcnow().isoformat()
                }
            }
        }
    }
    response = requests.patch(url, headers=headers, json=payload)
    if not response.ok:
        print(f"⚠️ Failed to update summary date — {response.text}")


