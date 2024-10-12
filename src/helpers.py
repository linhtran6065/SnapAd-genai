import firebase_admin
from firebase_admin import credentials, storage
import requests
from io import BytesIO
import base64

# Initialize Firebase app
cred = credentials.Certificate("data/snapad-firebase-adminsdk.json") 
firebase_admin.initialize_app(cred, {
    'storageBucket': 'snapad-12102024.appspot.com'  
})

def upload_image_to_firebase(local_file_path: str, firebase_file_name: str) -> str:
    bucket = storage.bucket()
    blob = bucket.blob(firebase_file_name)
    blob.upload_from_filename(local_file_path)

    # Make the image publicly accessible
    blob.make_public()

    print(f"Image uploaded to Firebase Storage: {blob.public_url}")
    return blob.public_url

def load_image_from_firebase(firebase_url: str):
    response = requests.get(firebase_url)
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        base64_image = base64.b64encode(image_data.getvalue()).decode('utf-8')
        return base64_image
    else:
        raise Exception(f"Failed to download image from Firebase. Status code: {response.status_code}")
        
def handle_gen_image_request(gen_image_request: dict):
    '''
    Example request:
    {
        "product_image_link" : "https://storage.googleapis.com/snapad-12102024.appspot.com/output/uploaded_image.jpg",
        "prompt" : "advertising photography of a bottle of perfume standing on water",
        "light_type" : "whitelight",
        "object_keyword" : "bottle",
        "save_id" : "1234569042740"
    }
    '''
    return { 
        "workflow_values": {
            "product_image": {"type": "image", "data": load_image_from_firebase(gen_image_request['product_image_link'])},
            "product_positive_prompt" : gen_image_request['prompt'],
            "product_negative_prompt" : "nsfw",
            "object_keyword" : gen_image_request['object_keyword'],
            "iclight_positive_prompt" : f"{gen_image_request['light_type']}, {gen_image_request['prompt']}",
            "iclight_negative_prompt" : "black and white"
        }
    }

# Example usage
if __name__ == "__main__":
    # Upload image example
    local_file = "data/replica-by-the-fireplice.jpg"
    uploaded_url = upload_image_to_firebase(local_file, "output/uploaded_image.jpg")
    print(f"Uploaded image URL: {uploaded_url}")

    # # Load image example
    # firebase_image_url = uploaded_url  
    # image_dat_base64 = load_image_from_firebase(firebase_image_url)
    # print("Image downloaded successfully")