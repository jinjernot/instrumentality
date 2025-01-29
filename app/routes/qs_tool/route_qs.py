from flask import Flask, request, render_template, send_from_directory

from app.routes.qs_tool.core.laptop.build_laptop import create_docx

import config

from config import QS_APP_PATH, QS_ZIP_FILE_PATH

# Create a Flask app
app = Flask(__name__)
app.use_static_for = 'static'

# Load config
app.config.from_object(config)

# Validate extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['VALID_FILE_EXTENSIONS']

def qs_tool():
    if request.method == 'POST':
        if 'qs_file' in request.files:
            file = request.files['qs_file']
            try:
                if allowed_file(file.filename):  # Check if the file has a valid extension
                    create_docx(file)  # Process the file
                    return send_from_directory(QS_APP_PATH, filename=QS_ZIP_FILE_PATH, as_attachment=True)  # Serve file for download
                else:
                    return render_template('error.html', error_message='Invalid file extension'), 400
            except Exception as e:
                return render_template('error.html', error_message=str(e)), 500  # Render error template for server errors
        else:
            return render_template('error.html', error_message='No file in the request'), 400

    # Render the form for GET requests
    return render_template('qs_tool.html')