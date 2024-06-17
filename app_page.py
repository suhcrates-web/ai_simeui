from flask import Flask, render_template, Response, request, session
from flask_cors import CORS
from datetime import datetime, timedelta
import binascii, codecs
import os
import time
from urllib.parse import unquote

app = Flask(__name__)
origins = [
    "http://localhost:5284",  # This is the origin of your client, change it if needed
    "http://165.132.142.56:5284/",
]
# CORS(app)
cors = CORS(app, resources={
    r"*": {
        "origins": "*",  # Adjust this as necessary for security
        # "methods": ["GET", "POST", "DELETE", "PUT"],  # Allowed methods
        # "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})
app.secret_key='1234'


@app.route(f'/test/', methods=['GET'])
def index_brod():
    return render_template('test_SSE_design.html')


@app.route('/set_data', methods=['POST'])
def set_data():
    session['data'] = request.form.get('data')
    return ''



if __name__ == "__main__":

    host = '0.0.0.0'
    port = 5234  # iteger 이어야함
    app.run(host=host, port=port, debug=True)
