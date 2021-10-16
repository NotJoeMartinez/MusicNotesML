import os, uuid
import datetime as dt
from flask import Flask, request, jsonify
from PIL import Image
import base64
from .predictions import make_predictions
import subprocess

app = Flask(__name__)

@app.route("/getnotes", methods=["POST", "GET"])
def process_image():

    secret_key_attempt = request.json["secret_key"]
    os_secret_key = os.environ['MSHACK_KEY']

    if secret_key_attempt != os_secret_key:
        print(secret_key_attempt)
        return "NOPE!!!"

    img_data = request.json['image']
    image_path = "API/uploads/"
    filename = f"{str(uuid.uuid1())}.png"
    full_img_path = image_path + filename

    with open(full_img_path, 'wb') as f:
        img_data = base64.b64decode(img_data)
        f.write(img_data)

    preds_dict = make_predictions(full_img_path)
    output_filename = preds_dict["overlayed_img_name"]  

    with open(output_filename, "rb") as f:
        b64_overlayed_img = base64.b64encode(f.read())
        b64_overlayed_img = b64_overlayed_img.decode('utf-8')

    print(preds_dict)

    return jsonify({
                    'image_path': full_img_path,
                    "notes_arr" : preds_dict["notes_arr"],
                    "b64_overylayed_img": b64_overlayed_img
                })



@app.route("/", methods=["POST", "GET"])
def test_gui():
    return "this is working"
    
if __name__ == "__main__":
    app.run(host='0.0.0.0')
