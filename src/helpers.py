import firebase_admin
from firebase_admin import credentials, storage
import base64
from io import BytesIO


def handle_gen_image_request(gen_image_request: dict):
    return { 
        "workflow_values": {
            "product_image": {"type": "image", "data": base64.b64encode(gen_image_request['product_image_data']).decode('utf-8')},
            "product_positive_prompt": gen_image_request['prompt'],
            "product_negative_prompt": "nsfw",
            "object_keyword": gen_image_request['object_keyword'],
            "iclight_positive_prompt": f"{gen_image_request['light_type']}, {gen_image_request['prompt']}",
            "iclight_negative_prompt": "black and white",
        }
    }

def handle_gen_video_request(gen_video_request: dict):
    print(f"*************************prompt:{gen_video_request['prompt']}")
    return { 
        "workflow_values": {
            "product_image": {"type": "image", "data": base64.b64encode(gen_video_request['product_image_data']).decode('utf-8')},
            "motion_positive_prompt": gen_video_request['prompt'],
            "motion_negative_prompt": "nsfw",
        }
    }

# ---- Firebase handle --------------
# Initialize Firebase app
cred = credentials.Certificate("data/snapad-firebase-adminsdk.json") 
firebase_admin.initialize_app(cred, {'storageBucket': 'snapad-12102024.appspot.com'})

def upload_image_to_firebase(local_file_path: str, firebase_file_name: str) -> str:
    try:
        bucket = storage.bucket()
        blob = bucket.blob(firebase_file_name)
        blob.upload_from_filename(local_file_path)
        blob.make_public()

        # Confirm the upload
        if blob.exists():
            print(f"Image uploaded to Firebase Storage: {blob.public_url}")
            return blob.public_url
        else:
            print("Upload failed: File does not exist in the bucket.")
            return ""
    except Exception as e:
        print(f"Error uploading image to Firebase: {e}")
        return ""


def load_image_from_firebase(firebase_url: str):
    response = requests.get(firebase_url)
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        base64_image = base64.b64encode(image_data.getvalue()).decode('utf-8')
        return base64_image
    else:
        raise Exception(f"Failed to download image from Firebase. Status code: {response.status_code}")
# ----------------------------------- 

def delete_file_in_folder(directory_path):
    import os
    import glob

    # Get all files in the directory
    files = glob.glob(os.path.join(directory_path, '*'))
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting {file}: {e}")

def check_file_exists_firebase(firebase_path: str) -> bool:
    """Check if a file exists in Firebase Storage.
    
    Args:
        firebase_path (str): Path to file in Firebase Storage
        
    Returns:
        bool: True if file exists, False otherwise
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(firebase_path)
        return blob.exists()
    except Exception as e:
        print(f"Error checking file existence in Firebase: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Upload image example
    local_file = "data/replica-by-the-fireplice.jpg"
    uploaded_url = upload_image_to_firebase(local_file, "replica-perfume-by-the-fireplace.jpg")
    print(f"Uploaded image URL: {uploaded_url}")

    # # Load image example
    # firebase_image_url = uploaded_url  
    # image_dat_base64 = load_image_from_firebase(firebase_image_url)
    # print("Image downloaded successfully")

def get_firebase_blob_url(firebase_path: str) -> str:
    """Get public URL for a Firebase Storage blob.
    
    Args:
        firebase_path (str): Path to file in Firebase Storage
        
    Returns:
        str: Public URL of the blob, empty string if error
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(firebase_path)
        return blob.public_url if blob.exists() else ""
    except Exception as e:
        print(f"Error getting blob URL: {e}")
        return ""
    
def b64_to_video(b64_str, file_path):
    video_data = base64.b64decode(b64_str.replace("data:video/mp4;base64,", ""))
    with open(file_path, "wb") as video_file:
        video_file.write(video_data)