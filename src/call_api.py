import requests
import uuid

# Define the file path and form data
file_path = "/Users/linhtran92/Desktop/PTIT/SnapAd-genai/src/data/innisfree-green-tea-cleansing-oil.jpg"
form_data = {
    "prompt": "advertising photography of a bottle of cleansing oil on a wood table",
    "light_type": "softlight",
    "object_keyword": "bottle",
    "save_id": str(uuid.uuid4())[-15:]
}

# Open the image file and send the POST request
with open(file_path, "rb") as image_file:
    response = requests.post(
        "http://113.22.56.109:1403/gen-image/jobs",
        files={"product_image": image_file},
        data=form_data
    )

# Print the response from the server
if response.status_code == 201:
    print("Job created successfully!")
    print(response.json())  # Should contain the job_id
else:
    print(f"Failed to create job. Status code: {response.status_code}")
    print(response.json())

'''
curl -X POST "http://113.22.56.109:1403/gen-image/jobs" \
-F "product_image=@/Users/linhtran92/Desktop/PTIT/SnapAd-genai/src/data/replica-by-the-fireplice.jpg" \
-F "prompt=advertising photography of a bottle of perfume standing on water" \
-F "light_type=softlight" \
-F "object_keyword=bottle" \
-F "save_id=171100"
'''

'''
curl -X GET "http://113.22.56.109:1403/gen-image/jobs/052ad3be-62a5-464d-b2c4-ae395899aae8/status"
'''