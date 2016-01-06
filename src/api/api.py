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
    append_if_exists(get_filter('file_type', request.args.get('file_type')), filters)
    append_if_exists(get_content_type_filter(request.args.get('content_type')), filters)
    append_if_exists(get_size_range_filter(
                        'size',
                        from_value=request.args.get('size_from'),
                        to_value=request.args.get('size_to')
                    ),filters)

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
    print(query_body)

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
    if field_name and filter_value and filter_value != 'all':
        return { 'term': { field_name: filter_value } }
    return None

def get_list_filter(field_name, filter_value):
    if field_name and filter_value and filter_value != 'all':
        return { 'terms': { field_name: filter_value } }
    return None

def get_size_range_filter(field_name, from_value=None, to_value=None):
    from_mb = None
    to_mb = None

    if from_value:
        from_mb = int(from_value) * 1024 * 1024
    if to_value:
        to_mb = int(from_value) * 1024 * 1024

    return get_range_filter(field_name, from_mb, to_mb)

def get_range_filter(field_name, from_value=None, to_value=None):
    if not field_name or (from_value is None and to_value is None):
        return None

    res = {
        'range': {
            field_name: {}
        }
    }

    if from_value:
        res['range'][field_name]['gte'] = from_value
    if to_value:
        res['range'][field_name]['gte'] = to_value

    return res

def get_content_type_filter(content_type):
    if content_type == 'video':
        return get_list_filter('extension', ['avi', 'wmv', 'mp4', 'mkv', 'flv', 'mov', 'mpg', 'rm', 'vob'])
    elif content_type == 'music':
        return get_list_filter('extension', ['mp3', 'wma', 'flac', 'ogg', 'wav', 'm4a', 'aac' ])
    elif content_type == 'document':
        return get_list_filter('extension', ['doc', 'docx', 'odt', 'txt', 'pdf', 'ppt', 'pptx', 'xls', 'xlsx' ])
    elif content_type == 'app':
        return get_list_filter('extension', ['exe', 'jar' ])
    elif content_type == 'iso':
        return get_filter('extension', 'iso')
    elif content_type == 'img':
        return get_list_filter('extension', ['jpg', 'png', 'jpeg', 'psd', 'gif', 'tiff'])
    return None


def run_api():
    app.run(host=app.config['API_HOST'], port=app.config['API_PORT'])
