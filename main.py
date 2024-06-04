from flask import Flask, send_file, render_template, request
from app.routes.image_tool.product_only import image_only
from app.routes.image_tool.annotated import annotated_only
import config

app = Flask(__name__)
app.static_folder = 'static'

app.config.from_object(config)

# Validate file extension 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['VALID_FILE_EXTENSIONS']

@app.route('/main')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/scs_tool')
def scs_tool():
    """SCS Tool page"""
    return render_template('scs_tool.html')

@app.route('/qs_tool')
def qs_tool():
    """QS Tool page"""
    return render_template('qs_tool.html')

@app.route('/image_tool', methods=['GET', 'POST'])
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
            print(e)
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
            print(e)
            return render_template('error.html', error_message=str(e)), 500  # Render error template for server errors
    else:
        if request.method == 'POST':
            return render_template('error.html', error_message='No file part in the request'), 400  # Render error template for missing file
    return render_template('image_tool.html')  # Render the form for GET requests


@app.route('/ds_tool')
def ds_tool():
    """DS Tool page"""
    return render_template('ds_tool.html')

if __name__ == "__main__":
    app.run(debug=True)
