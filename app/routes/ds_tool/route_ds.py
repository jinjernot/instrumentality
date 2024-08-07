from flask import Flask, request, render_template, send_from_directory

from app.routes.ds_tool.core.builder import create_ds

import config

from config import DF_APP_PATH

# Create a Flask app
app = Flask(__name__)
app.use_static_for = 'static'

# Load config
app.config.from_object(config)

# Validate extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['VALID_FILE_EXTENSIONS']

def ds_tool():
    if 'ds_file' in request.files:
        file = request.files['ds_file']
        try:
            if allowed_file(file.filename): 
                create_ds(file)  
                return send_from_directory(DF_APP_PATH, filename='ds.docx', as_attachment=True)   # Serve the zip file for download
            else:
                return render_template('error.html', error_message='Invalid file extension'), 400
        except Exception as e:
            return render_template('error.html', error_message=str(e)), 500  # Render error template for server errors
    else:
        if request.method == 'POST':
            return render_template('error.html', error_message='No file part in the request'), 400  # Render error template for missing file
    return render_template('ds_tool.html') 