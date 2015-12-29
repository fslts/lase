import config
import src.scanner as scanner

def main():
    scanner.scan(config.ranges)

if __name__ == '__main__':
    main()
