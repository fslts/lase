from flask import Flask
from flask import request, jsonify
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


@app.route('/search', methods=['GET'])
def search():
    queries = []

    append_if_exists(get_search_query(request.args.get('query')), queries)

    res = elastic_search(queries) if queries else None

    return jsonify({'success':True, 'data':res})

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
    return res['hits']['hits']


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
