import requests
import uuid

# Define the request payload
gen_image_request = {
    "product_image_link": "https://storage.googleapis.com/snapad-12102024.appspot.com/replica-perfume-by-the-fireplace.jpg",
    "prompt": "advertising photography of a bottle of perfume standing on water",
    "light_type": "whitelight",
    "object_keyword": "bottle",
    "save_id": str(uuid.uuid4())[-15:]
}

# Send the POST request to the FastAPI server
response = requests.post("http://113.22.56.109:1403/gen-image", json=gen_image_request)

# Print the response from the server
print(response.json())


'''
curl -X POST "http://113.22.56.109:1403/gen-image" \
     -H "Content-Type: application/json" \
     -d '{
           "product_image_link": "https://storage.googleapis.com/snapad-12102024.appspot.com/replica-perfume-by-the-fireplace.jpg",
           "prompt": "advertising photography of a bottle of perfume standing on a wood table",
           "light_type": "whitelight",
           "object_keyword": "bottle",
           "save_id": "1234567890"
         }'
'''

'''
curl -X POST "http://127.0.0.1:1403/gen-image" \
-F "product_image=@path/to/your/image.jpg" \
-F "prompt=advertising photography of a bottle of perfume standing on water" \
-F "light_type=whitelight" \
-F "object_keyword=bottle" \
-F "save_id=1234569042740"
'''