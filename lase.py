import sys
import getopt
import logging

import config
import src.producer as producer
import src.api as api


logger = logging.getLogger(__name__)


def help():
    print('lase.py [-s | -c | -a | --scan | --crawl | --api | --crawl-host [host] | --scan-host [host] ]')


def main(argv):
    if not argv:
        print('please choose one of the options')
        help()

    try:
        opts, args = getopt.getopt(argv, 'hsca', ['help', 'scan', 'crawl', 'crawl-host=', 'api'])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            help()
        elif opt in ('-a', '--api'):
            api.run_api()
        elif opt in ('-c', '--crawl'):
            producer.crawl_seq(config.ranges)
        elif opt in ('-s', '--scan'):
            producer.scan(config.ranges)
        elif opt == '--crawl-host':
            producer.crawl_seq([arg])
        elif opt == '--scan-host':
            producer.scan(config.ranges)


if __name__ == '__main__':
    # init mainly because of python 2
    reload(sys)
    sys.setdefaultencoding('utf-8')

    logging.basicConfig(stream=sys.stdout, level=logging.WARN)

    main(sys.argv[1:])
