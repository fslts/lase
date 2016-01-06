import sys
import time
import getopt

import config
import src.producer as producer
import src.api as api


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"sca",["scan","crawl","api"])
    except getopt.GetoptError:
        print('bad options')
        print 'lase.py [-s | -c | -a | --scan | --crawl | --api]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'lase.py [-s | -c | -a | --scan | --crawl | --api]'
        elif opt in ("-a", "--api"):
            api.run_api()
        elif opt in ("-c", "--crawl"):
            producer.crawl(config.ranges)
        elif opt in ("-s", "--scan"):
            producer.online_scan(config.ranges)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")

    main(sys.argv[1:])
