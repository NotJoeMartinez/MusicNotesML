
import uuid
import datetime as dt
from flask import Flask, request, jsonify
from PIL import Image
import base64


app = Flask(__name__)

@app.route("/get_notes", methods=["POST", "GET"])
def process_image():

    img_data = request.json['image']

    image_path = "API/uploads/"
    filename = f"{str(uuid.uuid1())}.png"
    full_img_path = image_path + filename

    with open(full_img_path, 'wb') as f:
        img_data = base64.b64decode(img_data)
        f.write(img_data)

    return jsonify({
                    'image_path': full_img_path 
                })



    
if __name__ == "__main__":
    app.run(debug=True)
