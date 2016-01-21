import json
import time
import math
from elasticsearch import Elasticsearch

import config.elastic as conf

def main():
    es = Elasticsearch()

    if es.indices.exists(conf.INDEX):
        es.indices.delete(conf.INDEX)

    if not es.indices.exists(conf.INDEX):
        es.indices.create(conf.INDEX, body={'setting':conf.SETTINGS,
                                            'mapping':conf.MAPPING_V2})

if __name__ == '__main__':
    main()
