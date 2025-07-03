from flask import Flask, render_template

from app.routes.image_tool.route_image import image_tool
from app.routes.scs_tool.route_scs import scs_tool
from app.routes.qs_tool.route_qs import qs_tool
from app.routes.ds_tool.route_ds import ds_tool

from app.utils.url_monitor_background import start_monitor_thread, url_statuses, status_lock, URLS_TO_MONITOR

import config

app = Flask(__name__)
app.static_folder = 'static'
app.config.from_object(config)


with status_lock: #
    for url in URLS_TO_MONITOR: #
        url_statuses[url] = {"is_up": None, "message": "N/A (Pending Check)", "last_checked": "N/A"} #


start_monitor_thread()

@app.route('/status')
def status_page():
    with status_lock: #
        current_statuses = dict(url_statuses) #
    
    return render_template('status_tool.html', statuses=current_statuses)

@app.route('/main')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/scs_tool', methods=['GET', 'POST'])
def scs_tool_route():
    """SCS Tool page"""
    return scs_tool()

@app.route('/qs_tool', methods=['GET', 'POST'])
def qs_tool_route():
    """QS Tool page"""
    return qs_tool()

@app.route('/image_tool', methods=['GET', 'POST'])
def image_tool_route():
    """Image Tool page"""
    return image_tool()
    
@app.route('/ds_tool', methods=['GET', 'POST'])
def ds_tool_route():
    """DS Tool page"""
    return ds_tool()

@app.route('/faq', methods=['GET', 'POST'])
def faq_route():
    """FAQ page"""
    return render_template('faq.html')

if __name__ == "__main__":
    app.run(debug=True)