from model.model import Model 
from model.helpers import b64_to_pil, pil_to_b64
import base64
import uuid
from PIL import Image
from fastapi import FastAPI

# load comfyui 
IM_MODEL = Model(port=8088)
IM_MODEL.load(ui_workflow="image_gen_workflow_api.json")

# Initialize FastAPI app
app = FastAPI()

@app.post("/gen-image")
async def gen_image(
    product_img_link: str, 
    gen_image_request: dict 
):
    # (**) TO-DO: handle gen image request
    # TO-DO: prepare image from link
    # (**) call to ComfyUI
    # TO-DO: upload image to firebase
    # TO-DO: return downloadable link 
    return link 


if __name__ == "__main__":
    import uvicorn
    # expose 1403 
    uvicorn.run(app, host="0.0.0.0", port=1403) # fastapi app will be running at port 1403