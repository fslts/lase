#ranges to be scanned in nmap format
ranges = [
    '147.175.176.2-254',
    '147.175.177.2-254',
    '147.175.178.2-254',
    '147.175.179.2-254',
    '147.175.180.2-254',
    '147.175.181.2-254',
    '147.175.182.2-254',
    '147.175.183.2-254',
    '147.175.186.2-254',
    '147.175.187.2-254',
    '147.175.192.2-254',
    '147.175.193.2-254',
    '147.175.194.2-254',
    '147.175.196.2-254',
    '147.175.197.2-254',
    '147.175.199.2-254',
    '147.175.189.2-254',
]

# stdout if empty
LOG_FILE = ''

INDEX = 'lase_alt'
DOC_TYPE = 'file'

SETTINGS =  {
    'analysis' : {
        'analyzer' : {
            'filename_words' : {
               'tokenizer' : 'filename',
               'filter' : ['asciifolding','lowercase']
            },
            'filename_ngram' : {
               'tokenizer' : 'filename',
               'filter' : ['asciifolding','lowercase','edge_ngram']
            }
        },
        'tokenizer' : {
            'filename' : {
                'pattern' : '[^\\p{L}\\d]+',
                'type' : 'pattern'
            }
        },
        'filter' : {
            'edge_ngram' : {
                'side' : 'front',
                'max_gram' : 20,
                'min_gram' : 1,
                'type' : 'edgeNGram'
            }
        }
    }
}

# mapping for version > 2 of elasticsearch
MAPPING_V2 = {
    'file' : {
        'properties' : {
            'filename' : {
                'type': 'multi_field',
                'fields': {
                    'partial': {
                        'type' : 'string',
                        'analyzer' : 'filename_ngram',
                        'search_analyzer' : 'filename_words'
                    },
                    'full': {
                        'type' : 'string',
                        'analyzer' : 'filename_words',
                    },
                }
            },

            'path': {
                'type': 'string',
                'analyzer' : 'filename_ngram',
                'search_analyzer' : 'filename_words'
            },
            'parent': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'host': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'file_type': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'extension': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'share_type': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'size': {
                'type': 'long'
            },
            'last_modified': {
                'type': 'date'
            },
            'crawled': {
                'type': 'date',
                'format': 'epoch_second'
            }
        }
    }
}

# mapping for pre 2 version of elasticsearch
MAPPING_V1 = {
    'file' : {
        'properties' : {
            'filename' : {
                'type': 'multi_field',
                'fields': {
                    'partial': {
                        'type' : 'string',
                        'index_analyzer' : 'filename_ngram',
                        'search_analyzer' : 'filename_words'
                    },
                    'full': {
                        'type' : 'string',
                        'analyzer' : 'filename_words'
                    },
                }
            },
            'path': {
                'type': 'string',
                'index_analyzer' : 'filename_ngram',
                'search_analyzer' : 'filename_words'
            },
            'parent': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'host': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'file_type': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'extension': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'share_type': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'size': {
                'type': 'long'
            },
            'last_modified': {
                'type': 'date'
            },
            'crawled': {
                'type': 'date',
                'format': 'epoch_second'
            }
        }
    }
}

API_HOST = '0.0.0.0'
API_PORT = 8080

# Statement for enabling the development environment
DEBUG = True

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Secret key for signing cookies
SECRET_KEY = "secret"


