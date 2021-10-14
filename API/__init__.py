import os, uuid
import datetime as dt
from flask import Flask, request, jsonify
from PIL import Image
import base64
from .predictions import make_predictions
import subprocess

app = Flask(__name__)

@app.route("/get_notes", methods=["POST", "GET"])
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

    with open(preds_dict["overlayed_img_path"], "rb") as f:
        b64_overlayed_img = base64.b64encode(f.read())
        b64_overlayed_img = b64_overlayed_img.decode('utf-8')


    return jsonify({
                    'image_path': full_img_path,
                    "notes_arr" : preds_dict["notes_arr"],
                    "b64_overylayed_img": b64_overlayed_img
                })



    
if __name__ == "__main__":
    app.run(debug=True)
