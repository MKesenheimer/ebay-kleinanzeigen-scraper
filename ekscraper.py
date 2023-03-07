#!/usr/bin/env python

import requests
import argparse
import time
import sys
import os
import datetime
import re
from enum import Enum
import statistics
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

__prog_name__ = 'ebay-Kleinanzeigen Scraper'
__version__ = 0.1

#outputdir="./"
outputdir="/mnt/volumes/usb/ebay-kleinanzeigen-data/"

def log(message):
    now = datetime.datetime.now()
    date_time = now.strftime("%d.%m.%Y %H:%M:%S: ")
    message = date_time + message
    print(message)
    # write message to file
    f = open(outputdir + "collection.log", 'a')
    f.write(message)
    f.write("\n")
    f.close()

class Status(Enum):
    ERROR   = 2,
    FAIL    = 1,
    SUCCESS = 0

def collect(cfg):
    term = '-'.join(cfg.sterm.lower().split())
    log("Searching for: {}".format(term))
    minpreis = cfg.minprice
    maxpreis = cfg.maxprice

    url = "https://www.ebay-kleinanzeigen.de:443/s-preis:{}:{}/{}/k0".format(minpreis, maxpreis, term)
    headers = {"GET /s-preis": "{}:{}/{}/k0 HTTP/2".format(minpreis, maxpreis, term), "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 "}
    try:
      r = requests.get(url, headers=headers)
    except:
      return Status.ERROR, [], []

    #print(r.text)
    parsed_html = BeautifulSoup(r.text, "html.parser")
    results = parsed_html.body.find_all('div', attrs={'class':'aditem-main'})

    status = Status.SUCCESS
    item_lst = []
    for item in results:
        try:
            ellipsis = item.find("a", class_="ellipsis", href=True)
            url = "https://www.ebay-kleinanzeigen.de" + ellipsis['href']
            title = ellipsis.text
            
            price = item.find("p", class_="aditem-main--middle--price-shipping--price").text.strip().encode("ascii", "ignore").decode("ascii").strip()
            price = re.findall('[0-9.]+',price)[0]
            descr = item.find("p", class_="aditem-main--middle--description").text
            position = ' '.join(item.find("div", class_="aditem-main--top--left").text.split())
            date = ' '.join(item.find("div", class_="aditem-main--top--right").text.split())
            
            if ("SUCHE" not in title.upper()) and ("SUCHE" not in descr.upper()):
                item_lst.append([title, descr, position, date, url,  price])
        except:
            status = Status.FAIL
            log("Warning: parsing failed.")
    header = ["title", "description", "place", "date", "url", "price"]
    return status, header, item_lst

def analyze(cfg, item_lst):
    header = ["time", "term", "search min price", "search max price", "number of items", "lowest price", "highest price", "average price"]
    prices = list(map(lambda x: int(x[-1]), item_lst))
    #print(prices)
    average = statistics.mean(prices)
    lowest = min(prices)
    highest = max(prices)
    data = [now.strftime("%Y-%m-%d %H:%M:%S"), cfg.sterm, str(cfg.minprice), str(cfg.maxprice), str(len(item_lst)), str(lowest), str(highest), str(round(average))]
    return Status.SUCCESS, header, data

def main():
    parser = argparse.ArgumentParser(description='%s version %.2f' % (__prog_name__, __version__))
    parser.add_argument('-s', '--search-term',
        action='store',
        metavar='<term>',
        dest='sterm',
        help='The term to search for.',
        default='')

    parser.add_argument('-l', '--min-price',
        action='store',
        metavar='<price>',
        dest='minprice',
        help='The minimal price of the item.',
        type=int,
        default=0)

    parser.add_argument('-u', '--max-price',
        action='store',
        metavar='<price>',
        dest='maxprice',
        help='The maximal price of the item.',
        type=int,
        default=1000)

    parser.add_argument('-i', '--intervall',
        action='store',
        metavar='<intervall>',
        dest='intervall',
        type=int,
        help='The time intervall in seconds to poll the data.',
        default=60)

    cfg = parser.parse_args()
    cfg.prog_name = __prog_name__

    pid = os.getpid()
    filename = outputdir + "process-" + '_'.join(cfg.sterm.lower().split()) + ".id"
    with open(filename, "w") as pidfile:  
        pidfile.write("{}".format(pid))

    log("Collecting data...")
    filename = outputdir + "data-" + '_'.join(cfg.sterm.lower().split()) + ".csv"
    log("Writing data to file {}.".format(filename))

    #print(data)
    prevStatus = Status.SUCCESS
    while True:
        status, _, item_lst = collect(cfg)
        if status == Status.FAIL:
            log("Scraping failed. Trying again in 60s.")
            time.sleep(60)

        elif status != Status.ERROR:
            if prevStatus != Status.SUCCESS:
                log("Continuing collecting data.")
        
            status, header, data = analyze(cfg, item_lst)
            # write data to file
            if os.path.isfile(filename):
                f = open(filename, 'a')
                f.write(",".join(data))
                f.write("\n")
                f.close()

            # if the file does not exist, create one and write the headers of the table to the first line
            else:
                f = open(filename, 'w')
                f.write("# ")
                f.write(",".join(header))
                f.write("\n")
                f.write(",".join(data))
                f.write("\n")
                f.close()

            time.sleep(cfg.intervall)

        else:
            log("General error occured. Trying again in 60s.")
            time.sleep(60)

        prevError = status

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log('Exiting...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
