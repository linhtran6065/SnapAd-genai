from io import BytesIO
import random
from pydantic import BaseModel
import requests
import base64
import requests
from PIL import Image
import json
import os
from urllib.parse import urlparse

# Define the data models
class CharacterConfig(BaseModel):
    ethnicity: str
    age: str
    body: str
    breast_size: str
    hair_style: str
    hair_color: str
    butt_size: str

class UserInput(BaseModel):
    naked: bool
    pose: str
    clothes: str
    location: str

class CreateImageRequest(BaseModel):
    character_config: CharacterConfig
    user_input: UserInput

def random_female_name():
    female_first_names = ["Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth", "Mila", "Ella", "Avery", "Sofia", "Camila", "Aria", "Scarlett"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"]
    # Generate a random full name
    first_name = random.choice(female_first_names)
    last_name = random.choice(last_names)
    full_name = first_name + " " + last_name
    return full_name

def handle_request_create_avatar(request: dict | CharacterConfig):
    location_list = ["Serene Garden", "Busy City Street", "Cozy Cafe", "Mountain Hike", "Historical Library", "Art Gallery", "Beach at Sunset", "Jungle", "Desert", "Bedroom", "Restaurant", "Club", "Snow", "Beach", "Oasis", "Casino", "Yacht", "Mountain", "Photo Studio"]

    character_config = request

    # gen prompt
    clothes = "clothes"
    location = random.choice(location_list)

    # character config
    ethnicity = character_config["ethnicity"] if character_config.get("ethnicity") else random.choice(["Caucasian", "Latina", "Asian", "Arab", "Black/Afro"])
    age = character_config["age"] if character_config.get("age") else random.choice(["18", "20", "30", "40", "50"])
    body = character_config["body"] if character_config.get("body") else random.choice(["Skinny", "Fit", "Chubby", "Muscular"])    
    breast_size = character_config["breast_size"] if character_config.get("breast_size") else random.choice(["Flat", "Small", "Medium", "Large", "Huge"])
    butt_size = character_config["butt_size"] if character_config.get("butt_size") else random.choice(["Small", "Medium", "Large", "Skinny", "Athletic"])
    hair_style = character_config["hair_style"] if character_config.get("hair_style") else random.choice(["Straight", "Braids", "Bangs", "Curly", "Bun", "Short", "Long", "Ponytail", "Pigtails"])
    hair_color = character_config["hair_color"] if character_config.get("hair_color") else random.choice(["Blonde", "Brunette", "Black", "Redhead", "Pink"])
    
    if hair_color.capitalize()=="Redhead" or hair_color.capitalize()=="Red":
        hair_color = "saturated ruby red"

    if breast_size.capitalize()=="Flat" or breast_size.capitalize()=="Small":
        breast_prompt = '(((flat is justice)))'
    else:
        breast_prompt = f'{breast_size} breast'

    if body.capitalize() == "Chubby":
        body = "obese"

    if int(age[0:2]) >= 50:
        face_prompt = "(very old face with wrinkles)"
    else:
        face_prompt = "cute face"

    positive_prompt = f'instagram full body photo of a {age} y.o woman, {face_prompt}, full face, soft natural shadow, studio lighting, {ethnicity} woman, {body} body, {breast_prompt}, {butt_size} butt, {hair_style} {hair_color} hair, in a {location}, ((wearing {clothes})), high details'

    name = random_female_name()
    eyes = random_female_name()
    mouth = random_female_name() 
    skin = random_female_name()
    style_face = random_female_name()
    shapeface= random_female_name()

    positive_prompt = "(( "+positive_prompt + " ))"+ "named " +name + ",eyes of " + eyes + ", mouth of " +mouth + ", skin of " + skin + ",style face of"+ style_face +",shape face of " + shapeface
    negative_prompt = """
                        (deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime), text, cropped, 
                        worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, 
                        poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, 
                        cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, 
                        too many fingers, long neck, netherhair
                    """

    seed = character_config.pop("seed", random.randint(1,9999999))
    steps = character_config.pop("steps", 6)
    cfg = character_config.pop("cfg", 1.5)

    return {
        "type": "create-avatar",
        "workflow_values": {"positive_prompt": positive_prompt, "negative_prompt": negative_prompt, "seed": seed, "steps": steps, "cfg": cfg}
    } 

def handle_request_create_image(avatar: str, create_image_request: dict):

    # Parse the URL
    parsed_url = urlparse(avatar)

    # Extract the file name
    person_image_object_key = os.path.basename(parsed_url.path)
    person_image_object_key = str(person_image_object_key)

    # check xem avatar tồn tại chưa?
    exist, e = check_object_exists(person_image_object_key)
    print(f'{person_image_object_key} exists: {exist}')
    print(f'Error: {e}')
    if not exist:
        return None

    character_config = create_image_request.pop("character_config")
    user_input = create_image_request.pop("user_input")

    # user input
    # if clothes detected then the naked should be False
    if user_input["clothes"] != "none":
        naked = ""
        clothes_prompt = f'wearing {user_input["clothes"]}'
    else:
        if user_input["naked"]:
            naked = "fully naked"
            clothes_prompt = ""
        else:
            naked = ""
            clothes_prompt = "wearing clothes"
    pose = "" if user_input.get("pose") == 'none' else user_input["pose"]
    location_prompt = "" if user_input.get("location") == 'none' else f'in a {user_input["location"]}'

    # character config
    ethnicity = character_config["ethnicity"] if character_config.get("ethnicity") else random.choice(["Caucasian", "Latina", "Asian", "Arab", "Black/Afro"])
    age = character_config["age"] if character_config.get("age") else random.choice(["18", "20", "30", "40", "50"])
    body = character_config["body"] if character_config.get("body") else random.choice(["Skinny", "Fit", "Chubby", "Muscular"])    
    breast_size = character_config["breast_size"] if character_config.get("breast_size") else random.choice(["Flat", "Small", "Medium", "Large", "Huge"])
    butt_size = character_config["butt_size"] if character_config.get("butt_size") else random.choice(["Small", "Medium", "Large", "Skinny", "Athletic"])
    hair_style = character_config["hair_style"] if character_config.get("hair_style") else random.choice(["Straight", "Braids", "Bangs", "Curly", "Bun", "Short", "Long", "Ponytail", "Pigtails"])
    hair_color = character_config["hair_color"] if character_config.get("hair_color") else random.choice(["Blonde", "Brunette", "Black", "Redhead", "Pink"])

    if hair_color.capitalize()=="Redhead" or hair_color.capitalize()=="Red":
        hair_color = "saturated ruby red"

    if breast_size.capitalize()=="Flat" or breast_size.capitalize()=="Small":
        breast_prompt = '(((flat is justice)))'
    else:
        breast_prompt = f'{breast_size} breast'

    if body.capitalize() == "Chubby":
        body = "obese"

    if int(age[0:2]) >= 50:
        face_prompt = "(very old face with wrinkles)"
    else:
        face_prompt = "cute face"

    positive_prompt = f'instagram full body {naked} photo of a {age} y.o woman, {location_prompt}, {pose}, {face_prompt}, soft natural shadow, studio lighting, {ethnicity} woman, {body} body, {breast_prompt}, {butt_size} butt, {hair_style} {hair_color} hair, {clothes_prompt}, high details'

    list_pussy = ["pussy", "hole", "vagina", "twat"]
    list_tits = ["tits", "bosom", "boobs", "titty", "breast"]
    list_ass = ["ass", "butt"]
    pussy, boobs, ass = False, False, False

    pussy = any(word in list_pussy for word in user_input["prompt"].split())
    boobs = any(word in list_tits for word in user_input["prompt"].split())
    ass = any(word in list_ass for word in user_input["prompt"].split())

    pre_prompt = f'instagram photo, {naked} photo of a {age} y.o woman, {face_prompt}, soft natural shadow, studio lighting, {ethnicity} woman, {body} body, {breast_prompt}, {butt_size} butt, {hair_style} {hair_color} hair, {location_prompt}, {clothes_prompt}, high details'
    if pussy:
        pose = "perfect pussy, pink vagina, beautiful vagina, legs spread"
        positive_prompt = f", (({pose})), {pre_prompt}"
    elif ass:
        pose = "standing naked, showing butt"
        positive_prompt = f", (({pose})), {pre_prompt}"
    elif boobs:
        pose = "showing boobs"
        positive_prompt = f", (({pose})), {pre_prompt}"

    negative_prompt = """
                        (deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime), text, cropped, 
                        worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, 
                        poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, 
                        cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, 
                        too many fingers, long neck, netherhair
                    """

    seed = create_image_request.pop("seed", random.randint(1,9999999))
    steps = create_image_request.pop("steps", 6)
    cfg = create_image_request.pop("cfg", 1.5)

    return {
        "type": "create-image",
        "workflow_values": {"positive_prompt": positive_prompt, "negative_prompt": negative_prompt, 
                            "seed": seed, "steps": steps, "cfg": cfg,
                            "person_image_object_key": person_image_object_key}
    }


def send_request_to_serverless(serverless_values: dict, model_id: str, api_key: str):
    # Call model endpoint
    resp = requests.post(
        f"https://api.runpod.ai/v2/{model_id}/runsync",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"input": serverless_values}
    )
    print("model id and api key:", model_id, api_key)

    return resp.json()

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

BUCKET_NAME = os.environ.get("BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
print("Bucket name and access key id", BUCKET_NAME, AWS_ACCESS_KEY_ID)
# Function to check if an object exists in the bucket
def check_object_exists(object_key):
    # Initialize a session using Amazon S3
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=object_key)
        return True, None
    except Exception as e:
        return False, e
