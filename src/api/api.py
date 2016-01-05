from flask import Flask
from flask import request, jsonify, render_template
import elasticsearch

#from config import elastic as elastic

app = Flask(__name__)
app.config.from_object('config.api')

#CORS
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def gui_search():
    return render_template('results.html', results=search())


@app.route('/api/search', methods=['GET'])
def api_search():
    return jsonify({'success':True, 'data':search()})


def search():
    queries = []
    append_if_exists(get_search_query(request.args.get('query')), queries)
    return transform_res(elastic_search(queries)) if queries else []


def transform_res(elastic_data):
    return [ item['_source'] for item in elastic_data['hits']['hits'] ]

def elastic_search(queries):
    es = elasticsearch.Elasticsearch()
    query = {
        'from' : 0,
        'size' : 20,
        'query' : {
            'bool': {
                'must': queries
            }
        }
    }
    #res = es.search(index=elastic.INDEX, body=query)
    res = es.search(index='lase_alt', body=query)
    return res


def append_if_exists(param, queries):
    if param:
        queries.append(param)

def get_search_query(term):
    if term:
        return {
            'simple_query_string' : {
                #'query': '"fried eggs" +(eggplant | potato) -frittata',
                'query': term,
                'fields': ['filename^2', 'path'],
                'default_operator': 'and',
                'minimum_should_match': '100%'
            }
        }
    return None

def run_api():
    app.run(host=app.config['API_HOST'], port=app.config['API_PORT'])
