from model.model import Model 
from model.helpers import b64_to_pil
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from helpers import handle_gen_image_request, upload_image_to_firebase, delete_file_in_folder, GenImageRequest
import os 

# load comfyui 
IM_MODEL = Model(port=8188)
IM_MODEL.load(ui_workflow="image_gen_workflow_api.json")

# Initialize FastAPI app
app = FastAPI()

@app.post("/gen-image")
async def gen_image(gen_image_request: dict | GenImageRequest):
    print("Request:", gen_image_request)

    gen_image_values = handle_gen_image_request(gen_image_request.dict()) 
    image_b64 = IM_MODEL.predict(gen_image_values)['result'][-1]['data']
    file_path = f"{gen_image_request['save_id']}.jpg"
    b64_to_pil(image_b64).save(file_path)
    
    result_link = upload_image_to_firebase(file_path, f"output/{file_path}")

    # delete uploaded files
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists("data/ComfyUI/output/"):
        delete_file_in_folder("data/ComfyUI/output/")
    return  result_link

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    # expose 1403, 8188
    uvicorn.run(app, host="0.0.0.0", port=1403) # fastapi app will be running at port 1403