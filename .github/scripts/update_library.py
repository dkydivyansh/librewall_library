import os
import json
import shutil
import cloudscraper
import subprocess
import sys
import tempfile
import shlex  # <--- Added shlex for safe shell quoting

# --- Configuration ---
REPO_OWNER = "dkydivyansh"
REPO_NAME = "librewall_library"
BRANCH = "main"
WALLPAPER_DIR = "wallpapers"
API_URL = "https://dkydivyansh.com/Project/api/wallpapers/?action=upd"

# Base URLs (Note: We will URL-encode spaces later for the JSON, but paths here are raw)
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}"
MEDIA_BASE = f"https://media.githubusercontent.com/media/{REPO_OWNER}/{REPO_NAME}/refs/heads/{BRANCH}"

def log(msg):
    print(msg, flush=True)

def run_git_command(command):
    try:
        # We don't use shlex.split here because we are constructing the command manually with quotes.
        # But we must ensure the command string is valid.
        subprocess.run(command, check=True, shell=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        log(f"Git error: {e.stderr}")

def get_wallpaper_type(config):
    # 1. Check for Video
    if config.get("videorender") is True and config.get("media"):
        return "2D/Video"
    # 2. Check for App / Interactive
    if config.get("htmlrender") is True and config.get("htmlWidgetFile"):
        return "App/Interactive"
    # 3. Check for 3D Model
    if "modelFile" in config or config.get("enable3DModel") is True:
        return "3D Scene"
    return "3D Scene"

def quote_path(path):
    """Wraps a path in quotes to handle spaces for shell commands."""
    return shlex.quote(path)

def url_encode(path_segment):
    """Encodes URL segments (e.g., spaces become %20)."""
    return requests.utils.quote(path_segment) if 'requests' in sys.modules else path_segment.replace(" ", "%20")

def main():
    # --- 1. Security Check ---
    api_token = os.environ.get("API_SECRET_TOKEN")
    if not api_token:
        log("Error: API_SECRET_TOKEN not found.")
        sys.exit(1)

    payload_list = []
    changes_made = False

    if not os.path.exists(WALLPAPER_DIR):
        log(f"Error: Directory '{WALLPAPER_DIR}' not found.")
        sys.exit(1)

    folders = [f for f in os.listdir(WALLPAPER_DIR) if os.path.isdir(os.path.join(WALLPAPER_DIR, f))]
    log(f"Scanning {len(folders)} folders...")

    for folder_name in folders:
        folder_path = os.path.join(WALLPAPER_DIR, folder_name)
        config_path = os.path.join(folder_path, "config.json")
        
        if not os.path.exists(config_path):
            continue

        try:
            with open(config_path, 'r') as f:
                content = f.read()
                clean_content = "\n".join([line for line in content.split('\n') if not line.strip().startswith("//")])
                config = json.loads(clean_content)
        except Exception as e:
            log(f"Error reading config for {folder_name}: {e}")
            continue

        # --- LOGIC: Check for ZIP ---
        zip_name = f"{folder_name}.zip"
        zip_path = os.path.join(folder_path, zip_name)

        is_new_item = False

        if not os.path.exists(zip_path):
            log(f"-> New Wallpaper: '{folder_name}' (Generating ZIP...)")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_zip_base = os.path.join(temp_dir, folder_name)
                # make_archive handles spaces in paths fine automatically
                shutil.make_archive(temp_zip_base, 'zip', folder_path)
                shutil.move(f"{temp_zip_base}.zip", zip_path)

            log(f"   ZIP Created.")
            
            # FIX: Use quoted path for git add
            quoted_zip_path = quote_path(zip_path)
            run_git_command(f"git add {quoted_zip_path}")
            
            changes_made = True
            is_new_item = True
        else:
            pass

        if is_new_item:
            metadata = config.get("metadata", {})
            thumb_relative = metadata.get("thumbnailImage", "thumb.gif")
            
            # FIX: URL Encode the folder name and file names for the API payload
            safe_folder_name = folder_name.replace(" ", "%20")
            safe_thumb_relative = thumb_relative.replace(" ", "%20")
            safe_zip_name = zip_name.replace(" ", "%20")

            thumb_url = f"{RAW_BASE}/{WALLPAPER_DIR}/{safe_folder_name}/{safe_thumb_relative}"
            zip_url = f"{MEDIA_BASE}/{WALLPAPER_DIR}/{safe_folder_name}/{safe_zip_name}"

            wallpaper_obj = {
                "Theme Name": metadata.get("themeName", folder_name),
                "Wallpaper Type": get_wallpaper_type(config),
                "Thumbnail URL": thumb_url,
                "ZIP URL": zip_url,
                "Author": metadata.get("author", "Unknown"),
                "Description": metadata.get("description", "")
            }
            payload_list.append(wallpaper_obj)

    # --- 3. Git Operations ---
    if changes_made:
        log("Pushing generated ZIP files to repo...")
        run_git_command('git config --global user.name "github-actions[bot]"')
        run_git_command('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        run_git_command('git commit -m "Auto-generate wallpaper ZIPs [skip ci]"')
        run_git_command('git push')
        log("Git push complete.")

    # --- 4. Send to API ---
    if len(payload_list) > 0:
        log(f"Sending {len(payload_list)} NEW wallpapers to API...")
        
        scraper = cloudscraper.create_scraper() 
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
            "Referer": "https://dkydivyansh.com/Project/admin.php" 
        }

        try:
            response = scraper.post(API_URL, json=payload_list, headers=headers)
            if response.status_code == 200:
                 log(f"Success! API Response: {response.text}")
            else:
                 log(f"API Failed: {response.status_code} - {response.text[:200]}...")
                 sys.exit(1)
        except Exception as e:
            log(f"Failed to send to API: {e}")
            sys.exit(1)
    else:
        log("No new wallpapers detected. Skipping API call.")

if __name__ == "__main__":
    main()
