import sys
import getopt
import logging

import config
import src.producer as producer
import src.api as api


logger = logging.getLogger(__name__)


def help():
    print('lase.py [-s [host] | -c [host] | -a | --scan [host] | --crawl [host] | --api]')

def main(argv):
    if not argv:
        print('please choose one of the options')
        help()

    try:
        opts, args = getopt.getopt(argv, "hsc:a", ["scan", "crawl", "api"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            help()
        elif opt in ("-a", "--api"):
            api.run_api()
        elif opt in ("-c", "--crawl") and not args:
            producer.crawl_seq(config.ranges)
        elif opt in ("-c", "--crawl"):
            producer.crawl_seq(args)
        elif opt in ("-s", "--scan") and not args:
            producer.scan(config.ranges)
        elif opt in ("-s", "--scan"):
            producer.scan(args)


if __name__ == '__main__':
    # init mainly because of python 2
    reload(sys)
    sys.setdefaultencoding("utf-8")

    logging.basicConfig(stream=sys.stdout, level=logging.WARN)

    main(sys.argv[1:])
