# LASE

| A LAN crawler and search engine

## Description

LASE is a crawler and search engine for files that are shared via FTP
or SMB.
Project has three elements:

1. scanner,
2. crawler,
3. API/UI.

### Scanner
Scans specified IP range and checks if SMB or FTP is open on these hosts. Results is used for two things. Crawler is scanning the range before every run so it can use it as an input and UI is scanning the range regularly so it can display the host online status in the search result.
`Nmap` is used for scanning and the results are stored in `redis`.

### Crawler
Crawls open ports on online hosts that were returned by scanner. Found files are then intexed to `elasticsearch`. After every run we delete data from previous crawling of the host since we don't want files that were removed in our index.

### API/UI
For communication with frontend there is a REST API available.
There is also a very simple UI.

## Installation

1. Install elastic search
2. Install redis
3. Install python dependencies with `pip -r requirements.txt`
4. Create config - copy config.py.sample to config.py and update it for your needs.
