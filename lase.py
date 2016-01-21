import sys
import getopt
import logging

import config
import src.producer as producer
import src.api as api


logger = logging.getLogger(__name__)


def main(argv):
    if not argv:
        print('please choose one of the options')
        print('lase.py [-s | -c | -a | --scan | --crawl | --api]')

    try:
        opts, args = getopt.getopt(argv, "hsca", ["scan", "crawl", "api"])
    except getopt.GetoptError:
        print('lase.py [-s | -c | -a | --scan | --crawl | --api]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('lase.py [-s | -c | -a | --scan | --crawl | --api]')
        elif opt in ("-a", "--api"):
            api.run_api()
        elif opt in ("-c", "--crawl"):
            producer.crawl_seq(config.ranges)
        elif opt in ("-s", "--scan"):
            producer.scan(config.ranges)


if __name__ == '__main__':
    # init mainly because of python 2
    reload(sys)
    sys.setdefaultencoding("utf-8")

    logging.basicConfig(stream=sys.stdout, level=logging.WARN)

    main(sys.argv[1:])
