import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from .scripts import encode_img, make_request, write_annotated 

UPLOAD_FOLDER = 'frontend/uploads'
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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], in_file_name))

        b64_string_out = encode_img(in_file_name, file_ext)
        b64_string_in = make_request(b64_string_out, instrament)
        write_annotated(b64_string_in, in_file_name)

        return redirect(url_for('show_fingers', name=in_file_name))

    return render_template('music_form.html')
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
 
    # '''

from flask import send_from_directory
@app.route('/uploads/<name>')
def show_fingers(name):

    #return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    return send_from_directory("uploads", name)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0')
