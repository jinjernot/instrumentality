from flask import Flask, request, render_template, send_from_directory
from app.routes.scs_tool.core.qa_data import clean_report, clean_report_granular
import asyncio
import config
from config import SCS_APP_PATH, SCS_GRANULAR_FILE_PATH

# Create a Flask app
app = Flask(__name__)
app.use_static_for = 'static'

# Load config
app.config.from_object(config)

# Validate extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['VALID_FILE_EXTENSIONS']

def scs_tool():
    if request.method == 'POST':
        if 'scs_regular' in request.files:
            file = request.files['scs_regular']
            try:
                if allowed_file(file.filename):
                    clean_report(file)
                    return send_from_directory(SCS_APP_PATH, filename='scs_qa.xlsx', as_attachment=True)
                else:
                    return render_template('error.html', error_message='Invalid file extension'), 400
            except Exception as e:
                return render_template('error.html', error_message=str(e)), 500

        elif 'scs_granular' in request.files:
            file = request.files['scs_granular']
            try:
                if allowed_file(file.filename):

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(clean_report_granular(file))

                    return send_from_directory(SCS_APP_PATH, filename='granular_qa.xlsx', as_attachment=True)
                else:
                    return render_template('error.html', error_message='Invalid file extension'), 400
            except Exception as e:
                return render_template('error.html', error_message=str(e)), 500
        else:
            return render_template('error.html', error_message='No file part in the request'), 400

    # Render the form for GET requests
    return render_template('scs_tool.html')