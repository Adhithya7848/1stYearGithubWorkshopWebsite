import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
REPO_NAME = os.getenv("REPO_NAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
CHECK_INTERVAL = os.getenv("CHECK_INTERVAL") # seconds between checks

# GitHub API base
API_URL = f"https://api.github.com/repos/{REPO_NAME}"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def get_open_pull_requests():
    url = f"{API_URL}/pulls"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def merge_pull_request(pr_number):
    url = f"{API_URL}/pulls/{pr_number}/merge"
    response = requests.put(url, headers=HEADERS, json={"merge_method": "merge"})
    if response.status_code == 200:
        print(f"✅ Merged PR #{pr_number}")
    else:
        print(f"❌ Failed to merge PR #{pr_number}: {response.json().get('message')}")


def is_mergeable(pr):
    # Get detailed PR info to check mergeable status
    pr_details = requests.get(pr["url"], headers=HEADERS).json()
    # Only return True if explicitly mergeable
    return pr_details.get("mergeable") is True


def main():
    print("🔄 Starting PR auto-merger...")

    while True:
        try:
            prs = get_open_pull_requests()
            if not prs:
                print("📭 No open PRs.")
            for pr in prs:
                pr_number = pr["number"]
                print(f"🔍 Checking PR #{pr_number}...")

                if is_mergeable(pr):
                    merge_pull_request(pr_number)
                else:
                    # Skip PR if not mergeable without printing warning
                    continue
        except Exception as e:
            print(f"⚠️ Error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
