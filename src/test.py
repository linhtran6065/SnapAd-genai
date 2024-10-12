from model.model import Model 
from model.helpers import b64_to_pil, pil_to_b64
import base64
from PIL import Image
import uuid

# load comfyui 
IM_MODEL = Model(port=8188)
IM_MODEL.load(ui_workflow="image_gen_workflow_api.json")
test_input = { 
  "type": "gen-image",
  "workflow_values": {
    "product_image": {"type": "image", "data": pil_to_b64(Image.open("data/replica-by-the-fireplice.jpg"))},
    "product_positive_prompt" : "advertising photography of a bottle of perfume standing on water",
    "product_negative_prompt" : "nsfw",
    "object_keyword" : "bottle",
    "iclight_positive_prompt" : "whitelight, advertising photography of a bottle of perfume standing on water",
    "iclight_negative_prompt" : "black and white"
  }
}
image_b64 = IM_MODEL.predict(test_input)['result'][-1]['data']
image = b64_to_pil(image_b64)
name = str(uuid.uuid4())[-15:]
file_path = f"{name}.png"
image.save(file_path)