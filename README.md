### **Set up command for GPU machine**
```bash
# connect to machine
ssh -L 8188:127.0.0.1:8188 tludemo@113.22.56.109

# create virtual env
conda deactivate
conda create --name snapad python=3.10
conda activate snapad

# set up comfyui
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# download custom nodes
cd custom_nodes/
# git clone https://github.com/ltdrdata/ComfyUI-Manager.git
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
git clone https://github.com/WASasquatch/was-node-suite-comfyui.git
git clone https://github.com/sipherxyz/comfyui-art-venture.git
git clone https://github.com/jamesWalker55/comfyui-various.git
git clone https://github.com/cubiq/ComfyUI_essentials.git
git clone https://github.com/kijai/ComfyUI-KJNodes.git
git clone https://github.com/kijai/ComfyUI-IC-Light.git
git clone https://github.com/storyicon/comfyui_segment_anything.git
cd ..

# download models
wget -P models/checkpoints/ https://huggingface.co/philz1337x/epicrealism/resolve/f22dc0ceeed8bd6d64a90b1e684ecd887aa37b40/epicrealism_naturalSinRC1VAE.safetensors

wget -P models/controlnet/ https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11f1p_sd15_depth_fp16.safetensors

mkdir models/diffusion_models/IC-Light/
wget -P models/diffusion_models/IC-Light/ https://huggingface.co/lllyasviel/ic-light/resolve/main/iclight_sd15_fc.safetensors

# expose fastapi port 
sudo ufw allow 1403
```

```python
# run comfyui
python3 main.py --listen --port 8188

python3 app.py
# run api

```

### **Input to workflow**
- Product image : product_image
- Prompt background : product_positive_prompt
- Negative prompt background : product_negative_prompt
- Keyword chỉ object : object_keyword
- Prompt IC-Light : iclight_positive_prompt
- Negative prompt IC-Light : iclight_negative_prompt

### **Input to image gen api**
- Product image link
- Prompt background
- Keyword chỉ object 
- Prompt Light type
- uuid (to name file store on firebase)