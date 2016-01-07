import multiprocessing

from . import crawler
from . import processor
from . import scanner

def _ranges_to_str(ranges):
    return ' '.join(ranges)


def _scan_host(host):

    cf = crawler.CrawlerFactory()
    proc = processor.LaseElasticImporter()

    for crwl in cf.produce(host, proc):
        crwl.crawl()

def scan(ranges):

    osf = scanner.OnlineScannerFactory()
    osc = osf.produce()

    scanned = osc.scan_range(_ranges_to_str(ranges))

    print(len(scanned))

    pool = multiprocessing.Pool(4)
    pool.map(_scan_host, scanned)

    #for host in scanned:
    #    _scan_host(host)

def online_scan(ranges):
    osf = scanner.OnlineScannerFactory()
    osc = osf.produce()

    scanned = osc.scan_range(_ranges_to_str(ranges))

    print(len(scanned))


