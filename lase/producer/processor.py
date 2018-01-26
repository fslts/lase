import time
import math
import logging
import datetime

import elasticsearch
from elasticsearch import helpers

import config

logger = logging.getLogger(__name__)

class Processor(object):

    def process(self, item):
        self._process(item)

    @staticmethod
    def produce(host):
        return LaseElasticImporter(host)


class LaseElasticImporter(Processor):

    def __init__(self, host):
        self._es = elasticsearch.Elasticsearch()
        self._crawled = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._host = host

        self._create_index()

    def _create_index(self):
        if not self._es.indices.exists(config.INDEX):
            self._es.indices.create(config.INDEX,
                                    body={'settings':config.SETTINGS,
                                          'mappings':config.MAPPING})


    def _process(self, lase_item):
        self._es.index(index=config.INDEX,
                       doc_type=config.DOC_TYPE,
                       id=lase_item.id,
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
        """ Method used to delete files that are no longer found in crawled
        host"""

        query = {
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            'must': [
                                {'range' : {
                                    'crawled' : {
                                        'lt' : self._crawled,
                                    }
                                }},
                                {'term': {
                                    'host': self._host.ip
                                }}
                            ]
                        }
                    }
                }
            }
        }

        # Elastic probably need to flush some changes, so we need to wait
        # a little. When there was no sleep records with correct time were
        # deleted
        time.sleep(1)

        to_delete = helpers.scan(self._es,
                                 query=query,
                                 index=config.INDEX,
                                 doc_type=config.DOC_TYPE)

        deleted = 0
        for item in to_delete:
            self._es.delete(index=config.INDEX, doc_type=config.DOC_TYPE, id=item['_id'])
            deleted += 1

        logger.info('deleted %s items for host %s', deleted, self._host.ip)
