from flask import Flask, send_file, render_template, request

from app.routes.image_tool.core.annotated import annotated_only
from app.routes.image_tool.core.product_only import image_only
from app.routes.image_tool.core.image_urls import image_url

import config

app = Flask(__name__)
app.static_folder = 'static'

app.config.from_object(config)

# Validate file extension 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['VALID_FILE_EXTENSIONS']

def image_tool():
    file_key_map = {
        'img_product_only': image_only,
        'img_annotated': annotated_only,
        'img_url': image_url
    }
    
    for file_key, processing_function in file_key_map.items():
        if file_key in request.files:
            file = request.files[file_key]
            try:
                if allowed_file(file.filename):
                    buffer, filename = processing_function(file)
                    if buffer:
                        return send_file(buffer, as_attachment=True, attachment_filename=filename, mimetype='application/zip' if file_key != 'img_url' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    else:
                        return render_template('error.html', error_message='Error processing the file'), 500
                else:
                    return render_template('error.html', error_message='Invalid file extension'), 400
            except Exception as e:
                return render_template('error.html', error_message=str(e)), 500

    if request.method == 'POST':
        return render_template('error.html', error_message='No file part in the request'), 400
    
    return render_template('image_tool.html')

if __name__ == "__main__":
    app.run(debug=True)
