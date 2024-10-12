from model.model import Model 
from model.helpers import b64_to_pil
from helpers import handle_gen_image_request, upload_image_to_firebase
import uuid
import os 


# load comfyui 
IM_MODEL = Model(port=8188) # có bắt buộc là 8088 không? 
IM_MODEL.load(ui_workflow="image_gen_workflow_api.json")
gen_image_request = {
    "product_image_link" : "https://storage.googleapis.com/snapad-12102024.appspot.com/output/uploaded_image.jpg",
    "prompt" : "advertising photography of a bottle of perfume standing on water",
    "light_type" : "whitelight",
    "object_keyword" : "bottle",
    "save_id" : str(uuid.uuid4())[-15:]
}
gen_image_values = handle_gen_image_request(gen_image_request)
print(gen_image_values)
image_b64 = IM_MODEL.predict(gen_image_values)['result'][-1]['data']
file_path = f"{gen_image_request['save_id']}.jpg"
b64_to_pil(image_b64).save(file_path)
result_link = upload_image_to_firebase(file_path, f"output/{file_path}")
# delete uploaded files
if os.path.exists(file_path):
    os.remove(file_path)
if os.path.exists("data/ComfyUI/output/"):
    os.remove("data/ComfyUI/output/*")
print(f"Result uploaded to: {result_link}")
