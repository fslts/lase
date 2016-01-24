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
