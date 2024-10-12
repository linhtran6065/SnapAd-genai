import runpod
from model.model import Model 
from model.helpers import b64_to_pil, pil_to_b64
import base64
import uuid
from aws_s3 import upload_file_to_s3, download_file_from_s3
from PIL import Image

def handler(job):
    if job['input']['type'] == 'create-avatar':
        image_b64 = CA_MODEL.predict(job['input'])['result'][-1]['data']
    
    elif job['input']['type'] == 'create-image':
        # lấy id của avatar để tải ảnh avatar 
        person_image_object_key = job['input']['workflow_values']['person_image_object_key']
        local_path = person_image_object_key
        download_file_from_s3(person_image_object_key, local_path)
        pil_img = Image.open(local_path)
        job['input']['workflow_values']['person_image'] = {"type": "image", "data": pil_to_b64(pil_img)}
        image_b64 = CI_MODEL.predict(job['input'])['result'][-1]['data']

    else: return "Invalid job type"
    image = b64_to_pil(image_b64)

    name = str(uuid.uuid4())[-15:]
    file_path = f"{name}.png"
    # Save the image
    image.save(file_path)

    s3_link = upload_file_to_s3(file_path)

    return s3_link

# CA_MODEL = Model(port=3000)
# CA_MODEL.load(ui_workflow="create_avatar_workflow.json")
IM_MODEL = Model(port=8088)
IM_MODEL.load(ui_workflow="image_gen_workflow_api.json")

# runpod.serverless.start({"handler": handler})