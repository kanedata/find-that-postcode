import csv
import urllib.request
import argparse
import os
from datetime import datetime
import os
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from metadata import NAME_FILES

AREA_LOOKUP = [
    ("cty15cd", "cty", "cty15nm"),
    ("lad15cd", "laua", "lad15nm"),
    ("wd15cd", "ward", None),
    ("par15cd", "parish", None),
    ("hlth12cd", "hlth", 'hlth12nm'),
    ("regd15cd", "rgd", "regd15nm"),
    ("rgn15cd", "rgn", "rgn15nm"),
    ("npark15cd", "park", "npark15nm"),
    ("bua11cd", "bua11", None),
    ("pcon15cd", "pcon", "pcon15nm"),
    ("eer15cd", "eer", "eer15nm"),
    ("pfa15cd", "pfa", "pfa15nm"),
]


def main():
    parser = argparse.ArgumentParser(description='Import area boundaries into elasticsearch.')

    # Postcode details
    parser.add_argument('placename_file', type=str, default='IPN_GB_2016',
                        help='Placename file to import')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='postcode', help='index used to store postcode data')

    args = parser.parse_args()

    placenames = []

    es = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)

    potential_env_vars = [
        "ELASTICSEARCH_URL",
        "ES_URL",
        "BONSAI_URL"
    ]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            es = Elasticsearch(os.environ.get(e_v))
            break

    placename_file = args.placename_file
    if not os.path.isfile(args.placename_file):
        print("[placenames] Downloading file: [%s]" % (placename_file))
        urllib.request.urlretrieve(placename_file, "data/placenames.csv")
        placename_file = "data/placenames.csv"

    with open(placename_file) as a:
        print("[placenames] Opening file: [%s]" % (placename_file))
        pcount = 0
        reader = csv.DictReader(a)
        for i in reader:
            i["_index"] = args.es_index
            i["_type"] = "placename"
            i["_op_type"] = "index"
            i["_id"] = i["place15cd"]

            for k in i:
                if i[k] == "":
                    i[k] = None

            # population count
            if i["popcnt"]:
                i["popcnt"] = int(i["popcnt"])

            # latitude and longitude
            for j in ["lat", "long"]:
                if i[j]:
                    i[j] = float(i[j])
                    if i[j] == 99.999999 or i[j] == 0:
                        i[j] = None
            if i["lat"] and i["long"]:
                i["location"] = {"lat": i["lat"], "lon": i["long"]}

            # get areas
            areas = {}
            for j in AREA_LOOKUP:
                if j[0] in i:
                    areas[j[1]] = i[j[0]]
                    del i[j[0]]
                    if j[2] and j[2] in i:
                        del i[j[2]]
            i["areas"] = areas

            placenames.append(i)
            pcount += 1

            if pcount % 100000 == 0:
                print("[placenames] Processed %s placenames" % pcount)
                print("[elasticsearch] %s placenames to save" % len(placenames))
                results = bulk(es, placenames)
                print("[elasticsearch] saved %s placenames to %s index" % (results[0], args.es_index))
                print("[elasticsearch] %s errors reported" % len(results[1]))
                placenames = []
        print("[placenames] Processed %s placenames" % pcount)
        print("[elasticsearch] %s placenames to save" % len(placenames))
        results = bulk(es, placenames)
        print("[elasticsearch] saved %s placenames to %s index" % (results[0], args.es_index))
        print("[elasticsearch] %s errors reported" % len(results[1]))
        placenames = []


if __name__ == '__main__':
    main()
