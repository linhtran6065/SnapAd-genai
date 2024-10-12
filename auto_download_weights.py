import requests
import os

def download_file(url, save_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {save_path}")
    else:
        print(f"Failed to download: {save_path}")

# List of model URLs and paths
import json 
with open('src/data/model.json', 'r') as file:
    models = json.load(file)

# Download each model
for model in models:
    download_file(model['url'], f"src/data/ComfyUI/{model['path']}")
