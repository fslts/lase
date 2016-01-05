import elasticsearch

import config.elastic as conf

class AbstractProcessor():

    def process(self, item):
        self._process(item)


class LaseElasticImporter(AbstractProcessor):

    def __init__(self):
        self._es = elasticsearch.Elasticsearch()

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
                             'last_modified':lase_item.last_modified})



