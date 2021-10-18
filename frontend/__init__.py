import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from .scripts import encode_img, make_request, write_annotated 

UPLOAD_FOLDER = 'frontend/static/uploads'
ANNOTATED_FOLDER = 'annotaed'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png','PNG', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        import logging
        logging.basicConfig(filename="instra.log", filemode="w")
        instrament = request.form['instrament']
        logging.error(f"{instrament}")
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        import uuid, pathlib
        file_ext = pathlib.Path(file.filename).suffix
        in_file_name = f"{str(uuid.uuid1())}{file_ext}"
        in_file_path = f"{app.config['UPLOAD_FOLDER']}/{in_file_name}"

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], in_file_name))

        encoded_img = encode_img(in_file_path, file_ext)
        api_responce = make_request(encoded_img, instrament)

        b64_responce = api_responce['b64_overylayed_img']
        note_names = api_responce['notes_arr']

        write_annotated(b64_responce, in_file_name)

        return redirect(url_for('show_fingers', overlayed_img=in_file_name,instrament=instrament))

    return render_template('music_form.html')
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
 
    # '''

from flask import send_from_directory
@app.route('/uploads/<overlayed_img>/<instrament>')
def show_fingers(overlayed_img, instrament):


    return render_template("display_overlayed.html",
    overlayed_img=overlayed_img, 
    instrament=instrament)
    #return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    # return send_from_directory("uploads", name)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0')
