import socket
import re

from flask import Flask
from flask import request, jsonify, render_template, url_for
import elasticsearch

import config
from src.utils.cache import LaseRedisCache
from pagination import Pagination

app = Flask(__name__)
app.config.from_object('config')


def url_for_other_page(page):
    args = request.args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


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
    res = search()

    page = int(request.args.get('page')) if request.args.get('page') else 1


    #TODO size param
    pagination = Pagination(page, 100, res['total'])
    return render_template('results.html',
        results=res,
        pagination=pagination
    )


@app.route('/api/search', methods=['GET'])
def api_search():
    return jsonify({'success':True, 'data':search()})


def search():
    query = get_search_query(request.args.get('query'))

    filters = []
    append_if_exists(get_host_filter(request.args.get('host')), filters)
    append_if_exists(get_filter('file_type', request.args.get('file_type')), filters)
    append_if_exists(get_content_type_filter(request.args.get('content_type')), filters)
    append_if_exists(get_size_range_filter(
                        'size',
                        from_value=request.args.get('size_from'),
                        to_value=request.args.get('size_to')
                    ),filters)

    page = int(request.args.get('page')) if request.args.get('page') else 1
    return transform_res(elastic_search(query, page, filters)) if query else null_result()

def null_result():
    return { 'total':0, 'items':[] }

def transform_res(elastic_data):
    return {
        'total': elastic_data['hits']['total'],
        'items': transform_hits(elastic_data['hits']['hits'])
    }

def transform_hits(hits):
    res = []
    cache = LaseRedisCache()
    for item in hits:
        final_item = item['_source']
        final_item['online'] = len(cache.load_host(final_item['host'])) > 0
        res.append(final_item)
    return res

def elastic_search(query_str, page, filters = None):
    es = elasticsearch.Elasticsearch()

    query_body = {}
    #TODO size param
    query_body['from'] = (page - 1) * 100
    query_body['size'] = 100

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

    return es.search(index=config.INDEX, body=query_body)


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

def get_host_filter(host):
    return get_filter('host', normalize_host(host))

def normalize_host(host):
    if not host:
        return None
    if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', host):
        return host
    else:
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
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
        to_mb = int(to_value) * 1024 * 1024

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
        res['range'][field_name]['lte'] = to_value

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
