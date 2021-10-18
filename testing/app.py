import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from scripts import encode_img, make_request, write_annotated 

UPLOAD_FOLDER = 'uploads'
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
        b64_string_in = make_request(b64_string_out)
        write_annotated(b64_string_in, in_file_name)

        return redirect(url_for('show_fingers', name=in_file_name))

    return render_template('music_form.html')

from flask import send_from_directory
@app.route('/frontend/uploads/<name>')
def show_fingers(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)