from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = 'static'

@app.route('/instrumentality')
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

@app.route('/image_tool')
def image_tool():
    """Image Tool page"""
    return render_template('image_tool.html')

@app.route('/ds_tool')
def ds_tool():
    """DS Tool page"""
    return render_template('ds_tool.html')

if __name__ == "__main__":
    app.run(debug=True)
