import requests
import json
from datetime import datetime, timedelta
import argparse

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--user', help='Github username')
args = parser.parse_args()

username = args.user

# API endpoint for user events
url = f"https://api.github.com/users/{username}/events"

# Calculate start time as one week ago
start_time = datetime.now() - timedelta(days=7)
start_time_hum = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# Send GET request to API endpoint with time filter
response = requests.get(url, params={'per_page': '100', 'since': start_time})

# Check if response was successful
if response.status_code == 200:
    events = json.loads(response.content)

    # Create a dictionary to store events by repo
    event_dict = {}

    # Sort events by repo name
    events = sorted(events, key=lambda e: e['repo']['name'])

    for event in events:
        # Check if event occurred within last week
        event_time = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        if event_time >= start_time:
            repo = event['repo']['name']
            if repo in event_dict:
                event_dict[repo].append(event)
            else:
                event_dict[repo] = [event]

    for repo_name, events in event_dict.items():
        entries = []

        for event in events:
            event_type = event['type']

            if event_type == 'IssuesEvent':
                action = event['payload']['action']
                if action == 'opened':
                    desc = "issue " + action
                    payload = event['payload']['issue']
                else:
                    continue
            elif event_type == 'PullRequestEvent':
                action = event['payload']['action']
                if action == 'opened':
                    desc = "PR " + action
                    payload = event['payload']['pull_request']
                else:
                    continue
            elif event_type == 'PullRequestReviewEvent':
                action = event['payload']['action']
                if action == 'created':
                    desc = "PR reviewed"
                    payload = event['payload']['pull_request']
                else:
                    continue
            elif event_type == 'ReleaseEvent':
                action = event['payload']['action']
                if action == 'published':
                    desc = "release " + action
                    payload = event['payload']['release']
                else:
                    continue
            else:
                continue

            entry = f"{desc}: [{payload['title']}]({payload['html_url']})"
            entries.append((event_type, entry))

        if entries:
            print(f"\n- {repo_name}")
            print(f"  - @{username} (XX days)")

        for (event_type, entry) in entries:
            print(f"  - {entry}")

else:
    print(f"Error: Could not retrieve events for user {username}")
