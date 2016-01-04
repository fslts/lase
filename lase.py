import sys
import time
import multiprocessing

import config
import src.scanner as scanner
import src.crawler as crawler
import src.processor as processor


def _ranges_to_str(ranges):
    return ' '.join(ranges)


def _scan_host(host):

    cf = crawler.CrawlerFactory()
    proc = processor.LaseElasticProcessor()

    print(host.full_host_name())
    for crwl in cf.produce(host, proc):
        crwl.crawl()


def scan(ranges):
    start = time.time()

    osf = scanner.OnlineScannerFactory()
    osc = osf.produce()

    scanned = osc.scan_range(_ranges_to_str(ranges))

    print(time.time() - start)
    print(len(scanned))

    #pool = multiprocessing.Pool(4)
    #pool.map(_scan_host, scanned)

    for host in scanned:
        _scan_host(host)

    print(time.time() - start)


def main():

    reload(sys)
    sys.setdefaultencoding("utf-8")

    scan(config.ranges)


if __name__ == '__main__':
    main()
