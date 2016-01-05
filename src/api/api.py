from flask import Flask
from flask import request, jsonify

app = Flask(__name__)
app.config.from_object('config.api')

#CORS
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response


@app.route('/search', methods=['GET'])
def search():
    return jsonify({'success':True})

def run_api():
    app.run(host=app.config['API_HOST'], port=app.config['API_PORT'])
