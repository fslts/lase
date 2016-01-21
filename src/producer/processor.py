import time
import math

import elasticsearch
from elasticsearch import helpers

import config.elastic as conf

class AbstractProcessor():

    def process(self, item):
        self._process(item)


class LaseElasticImporter(AbstractProcessor):

    def __init__(self, host):
        self._es = elasticsearch.Elasticsearch()
        self._crawled = math.floor(time.time())
        self._host = host

    def _process(self, lase_item):
        self._es.index(index=conf.INDEX,
                       doc_type=conf.DOC_TYPE,
                       id=lase_item.id(),
                       body={'filename':lase_item.filename,
                             'path':lase_item.path,
                             'parent':lase_item.parent,
                             'host':lase_item.host,
                             'share_type':lase_item.share_type,
                             'size':lase_item.size,
                             'file_type':lase_item.file_type,
                             'extension':lase_item.extension,
                             'last_modified':lase_item.last_modified,
                             'crawled':self._crawled})

    def cleanup(self):
        query = {
            'query': {
                'range' : {
                    'crawled' : {
                        'lt' : self._crawled,
                    }
                }
            }
        }

        to_delete = helpers.scan(self._es,
                        query=query,
                        index=conf.INDEX,
                        doc_type=conf.DOC_TYPE)

        for item in to_delete:
            print(item)
        #   self._es.delete(index=conf.INDEX, doc_type=conf.DOC_TYPE, id=item['_id'])
