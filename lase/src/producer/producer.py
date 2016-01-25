import multiprocessing
import logging

from . import crawler
from . import processor
from . import scanner


logger = logging.getLogger(__name__)


def crawl(ranges):

    scanned = scan(ranges)

    pool = multiprocessing.Pool(4)
    pool.map(_scan_host, scanned)


def crawl_seq(ranges):
    """Sequential host crawling. Mainly for debugging purposes"""

    scanned = scan(ranges)

    for host in scanned:
        _scan_host(host)


def scan(ranges):

    osf = scanner.OnlineScannerFactory()
    osc = osf.produce()

    scanned = osc.scan_range(_ranges_to_str(ranges))

    logging.info('scanned; %s hosts found' % (len(scanned),))

    return scanned


def _ranges_to_str(ranges):
    return ' '.join(ranges)


def _scan_host(host):

    cf = crawler.CrawlerFactory()
    proc = processor.LaseElasticImporter(host)

    for crwl in cf.produce(host, proc):
        crwl.crawl()

    proc.cleanup()
