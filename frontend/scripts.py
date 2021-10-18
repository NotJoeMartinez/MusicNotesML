


import requests
from requests.structures import CaseInsensitiveDict
import base64, json, os

def encode_img(file_path, ext="png"):

    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    
    encoded_string = encoded_string.decode('utf-8')
    return encoded_string


def make_request(b64_string, instrament):
    url = "http://40.121.3.69/getnotes"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    os_secret_key = os.environ['MSHACK_KEY']
    raw_data = {
        'image': b64_string,
        "secret_key": os_secret_key, 
        "instrament": instrament 
        }

    json_data = json.dumps(raw_data, indent=2)

    resp = requests.post(url, headers=headers, data=json_data)
    resp = resp.json()
    return resp



def write_annotated(b64_string, og_img_name):
    # import logging
    # logging.basicConfig(filename="sripts.log", filemode='w')

    out_filepath = f"frontend/static/uploads/{og_img_name}"
    # logging.error(f"{out_filepath}\n{og_img_name} \n{b64_string}")

    imgdata = base64.b64decode(b64_string)

    with open(out_filepath, "wb") as f:
        f.write(imgdata)

