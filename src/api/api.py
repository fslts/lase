from flask import Flask
from flask import request, jsonify, render_template
import elasticsearch

from config import elastic as elastic

app = Flask(__name__)
app.config.from_object('config.api')

#CORS
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers',
                       'Content-Type,Authorization')
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
    query = get_search_query(request.args.get('query'))

    filters = []
    append_if_exists(get_filter('host', request.args.get('host')), filters)

    return transform_res(elastic_search(query, filters)) if query else None


def transform_res(elastic_data):
    return [ item['_source'] for item in elastic_data['hits']['hits'] ]

def elastic_search(query_str, filters = None):
    es = elasticsearch.Elasticsearch()

    query_body = {}
    query_body['from'] = 0
    query_body['size'] = 20

    query_body['query'] = {}
    query_body['query']['filtered'] = {
        'query': query_str
    }

    if filters:
        query_body['query']['filtered']['filter'] = {
            'bool': {
                'must': filters
            }
        }

    return es.search(index=elastic.INDEX, body=query_body)


def append_if_exists(param, queries):
    if param:
        queries.append(param)

def get_search_query(term):
    if term:
        return {
            'bool': {
                'should': [
                    {'multi_match' : {
                        'query': term,
                        'fields': ['filename^2', 'path'],
                        'operator': 'and',
                    }},
                    {'multi_match' : {
                        'query': term,
                        'fields': ['filename^2', 'path'],
                        'operator': 'and',
                        'fuzziness': 'AUTO',
                        'boost':0.2
                    }}
                ]
            }
        }
    return None

def get_filter(field_name, filter_value):
    if field_name and filter_value:
        return { "term": { field_name: filter_value } }
    return None

def run_api():
    app.run(host=app.config['API_HOST'], port=app.config['API_PORT'])
