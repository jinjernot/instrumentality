from flask import Flask, send_file, render_template, request

from app.routes.image_tool.core.product_only import image_only
from app.routes.image_tool.core.annotated import annotated_only
from app.routes.image_tool.core.image_urls import image_url

import config

app = Flask(__name__)
app.static_folder = 'static'

app.config.from_object(config)

# Validate file extension 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['VALID_FILE_EXTENSIONS']

def image_tool():
    if 'img_product_only' in request.files:
        file = request.files['img_product_only']
        try:
            if allowed_file(file.filename):  # Check if the file has a valid extension
                zip_buffer, zip_filename = image_only(file)  # Process the file and get the zip buffer and filename
                if zip_buffer:
                    return send_file(zip_buffer, as_attachment=True, attachment_filename=zip_filename, mimetype='application/zip')  # Serve the zip file for download
                else:
                    return render_template('error.html', error_message='Error processing the file'), 500  # Render error template for processing errors
            else:
                return render_template('error.html', error_message='Invalid file extension'), 400  # Render error template for invalid file extension
        except Exception as e:
            return render_template('error.html', error_message=str(e)), 500  # Render error template for server errors
        
    elif 'img_annotated' in request.files:  # Check for img_annotated
        file = request.files['img_annotated']
        try:
            if allowed_file(file.filename):  # Check if the file has a valid extension
                zip_buffer, zip_filename = annotated_only(file)  # Process the file and get the zip buffer and filename
                if zip_buffer:
                    return send_file(zip_buffer, as_attachment=True, attachment_filename=zip_filename, mimetype='application/zip')  # Serve the zip file for download
                else:
                    return render_template('error.html', error_message='Error processing the file'), 500  # Render error template for processing errors
            else:
                return render_template('error.html', error_message='Invalid file extension'), 400  # Render error template for invalid file extension
        except Exception as e:
            return render_template('error.html', error_message=str(e)), 500  # Render error template for server errors
        
    elif 'img_url' in request.files:  # Check for img_annotated
        file = request.files['img_url']
        try:
            if allowed_file(file.filename):  # Check if the file has a valid extension
                excel_buffer, excel_filename = image_url(file)  # Process the file and get the zip buffer and filename
                if excel_buffer:
                    return send_file(excel_buffer, as_attachment=True, attachment_filename=excel_filename)  # Serve the zip file for download
                else:
                    return render_template('error.html', error_message='Error processing the file'), 500  # Render error template for processing errors
            else:
                return render_template('error.html', error_message='Invalid file extension'), 400  # Render error template for invalid file extension
        except Exception as e:
            return render_template('error.html', error_message=str(e)), 500  # Render error template for server errors
    else:
        if request.method == 'POST':
            return render_template('error.html', error_message='No file part in the request'), 400  # Render error template for missing file
    return render_template('image_tool.html')  # Render the form for GET requests