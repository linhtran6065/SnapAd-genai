import requests
import uuid

# Define the request payload
gen_image_request = {
    "product_image_link": "https://storage.googleapis.com/snapad-12102024.appspot.com/output/uploaded_image.jpg",
    "prompt": "advertising photography of a bottle of perfume standing on water",
    "light_type": "whitelight",
    "object_keyword": "bottle",
    "save_id": str(uuid.uuid4())[-15:]
}

# Send the POST request to the FastAPI server
response = requests.post("http://113.22.56.109:1403/gen-image", json=gen_image_request)

# Print the response from the server
print(response.json())