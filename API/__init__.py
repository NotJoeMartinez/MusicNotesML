
import uuid
import datetime as dt
from flask import Flask, request, jsonify
from PIL import Image
import base64


app = Flask(__name__)

@app.route("/get_string", methods=["POST"])
def process_image():
    # file = request.files['image']
    import logging 
    logging.basicConfig(filename="app.log", filemode="w")
    rs = request.files
    dir(rs)

    logging.error(f"rs: {rs}, {type(rs)}")

    with open("imageToSave.png", "wb") as fh:
        fh.write(base64.decodebytes(rs))

    print(rs, type(rs))
    # Read the image via file.stream
    # img = Image.open(file.stream)
    # file_name = f"API/predictions/uploads/{str(uuid.uuid1())}.png"
    # img.save(file_name)

    # return jsonify({
                    # 'file_dir': file_name, 
                    # 'Image Size': [img.width, img.height]})
    return rs 



    
if __name__ == "__main__":
    app.run(debug=True)
