import os
import json
import shutil
import requests
import subprocess
import sys

REPO_OWNER = "dkydivyansh"
REPO_NAME = "librewall_library"
BRANCH = "main"
WALLPAPER_DIR = "wallpapers"
API_URL = "https://dkydivyansh.com/Project/api/wallpapers/?action=upd"

# Base URLs
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}"
MEDIA_BASE = f"https://media.githubusercontent.com/media/{REPO_OWNER}/{REPO_NAME}/refs/heads/{BRANCH}"

def run_git_command(command):
    """Runs a git command and handles errors."""
    try:
        subprocess.run(command, check=True, shell=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr}")

def get_wallpaper_type(config_data):
    if "modelFile" in config_data:
        return "3D Scene"
    return "2D/Video"

def main():
    api_token = os.environ.get("API_SECRET_TOKEN")
    
    if not api_token:
        print("Error: API_SECRET_TOKEN not found in environment variables.")
        sys.exit(1)

    payload_list = []
    changes_made = False

    if not os.path.exists(WALLPAPER_DIR):
        print(f"Error: Directory '{WALLPAPER_DIR}' not found.")
        sys.exit(1)

    for folder_name in os.listdir(WALLPAPER_DIR):
        folder_path = os.path.join(WALLPAPER_DIR, folder_name)

        if not os.path.isdir(folder_path):
            continue

        config_path = os.path.join(folder_path, "config.json")
        
        if not os.path.exists(config_path):
            continue

        try:
            with open(config_path, 'r') as f:
                content = f.read()
                clean_content = "\n".join([line for line in content.split('\n') if not line.strip().startswith("//")])
                config = json.loads(clean_content)
        except Exception as e:
            print(f"Error reading config for {folder_name}: {e}")
            continue

        zip_name = f"{folder_name}.zip"
        zip_path = os.path.join(folder_path, zip_name)

        if not os.path.exists(zip_path):
            print(f"Creating missing ZIP for: {folder_name}")
            shutil.make_archive(os.path.join(folder_path, folder_name), 'zip', folder_path)
            run_git_command(f"git add {zip_path}")
            changes_made = True

        metadata = config.get("metadata", {})
        thumb_relative = metadata.get("thumbnailImage", "thumb.gif")
        
        thumb_url = f"{RAW_BASE}/{WALLPAPER_DIR}/{folder_name}/{thumb_relative}"
        zip_url = f"{MEDIA_BASE}/{WALLPAPER_DIR}/{folder_name}/{zip_name}"

        wallpaper_obj = {
            "Theme Name": metadata.get("themeName", folder_name),
            "Wallpaper Type": get_wallpaper_type(config),
            "Thumbnail URL": thumb_url,
            "ZIP URL": zip_url,
            "Author": metadata.get("author", "Unknown"),
            "Description": metadata.get("description", "")
        }
        
        payload_list.append(wallpaper_obj)

    if changes_made:
        print("Pushing generated ZIP files to repo...")
        run_git_command('git config --global user.name "github-actions[bot]"')
        run_git_command('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        run_git_command('git commit -m "Auto-generate wallpaper ZIPs [skip ci]"')
        run_git_command('git push')

    print(f"Sending {len(payload_list)} wallpapers to API...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}" 
    }

    try:
        response = requests.post(API_URL, json=payload_list, headers=headers)
        if response.status_code == 200:
             print(f"Success! API Response: {response.text}")
        else:
             print(f"API Failed: {response.status_code} - {response.text}")
             sys.exit(1)
    except Exception as e:
        print(f"Failed to send to API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
