import requests
import os
import json
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file
load_dotenv(find_dotenv("../../../.env"))

# Get the GitHub token from environment variables
# print(os.environ.get('GITHUB_TOKEN'))
github_token = os.getenv('GITHUB_TOKEN')
print(f"Loaded GitHub token: {github_token}")

if not github_token:
    raise ValueError("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")

def get_contribution_activity(username, token):
    url = f"https://api.github.com/users/{username}/events/public"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        events = response.json()
        contributions = []
        for event in events:
            if event['type'] in ['PushEvent', 'IssuesEvent', 'PullRequestEvent']:
                contributions.append({
                    "type": event['type'],
                    "repo": event['repo']['name'],
                    "time": event['created_at']
                })
        return contributions
    else:
        return f"Error: {response.status_code} - {response.text}"

# Replace with your username and token
username = "torvalds"
activity = get_contribution_activity(username, github_token)

# Ensure the output directory exists
output_dir = "_output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Write the activity to a JSON file
output_file = f"{output_dir}/{username}-github-activity.json"
with open(output_file, "w") as f:
    json.dump(activity, f)

print(f"Wrote {output_file}")