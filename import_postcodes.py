import csv
import zipfile
import io
import argparse
import os
from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from metadata import NAME_FILES


def main():
    parser = argparse.ArgumentParser(description='Import postcodes into elasticsearch.')

    # Postcode details
    parser.add_argument('nspl', type=str,
                        default='data/NSPL.zip',
                        help='ZIP file for National Statistics Postcode Lookup')
    parser.add_argument('--skip-postcodes', dest='do_postcodes', action='store_false', help="Skip import of the postcode data")
    parser.add_argument('--skip-codes', dest='do_codes', action='store_false', help="Skip import of the names and codes data")

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')

    args = parser.parse_args()

    postcodes = []

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

    code_files = [i["file"] for i in NAME_FILES]

    with zipfile.ZipFile(args.nspl) as pczip:
        for f in pczip.filelist:
            if f.filename.endswith(".csv") and f.filename.startswith("Data/multi_csv/NSPL_") and args.do_postcodes:
                print("[postcodes] Opening %s" % f.filename)
                pcount = 0
                with pczip.open(f, 'r') as pccsv:
                    pccsv = io.TextIOWrapper(pccsv)
                    reader = csv.DictReader(pccsv)
                    for i in reader:
                        # Skip Northern Irish postcodes as not allowed by license
                        # https://www.ons.gov.uk/methodology/geography/licences
                        if i["pcds"].lower().startswith('bt'):
                            continue

                        i["_index"] = "geo_postcode"
                        i["_type"] = "_doc"
                        i["_op_type"] = "index"
                        i["_id"] = i["pcds"]

                        # null any blank fields
                        for k in i:
                            if i[k] == "":
                                i[k] = None

                        # date fields
                        for j in ["dointr", "doterm"]:
                            if i[j]:
                                i[j] = datetime.strptime(i[j], "%Y%m")

                        # latitude and longitude
                        for j in ["lat", "long"]:
                            if i[j]:
                                i[j] = float(i[j])
                                if i[j] == 99.999999:
                                    i[j] = None
                        if i["lat"] and i["long"]:
                            i["location"] = {"lat": i["lat"], "lon": i["long"]}

                        # integer fields
                        for j in ["oseast1m", "osnrth1m", "usertype", "osgrdind", "imd"]:
                            if i[j]:
                                i[j] = int(i[j])
                        postcodes.append(i)
                        pcount += 1

                        if pcount % 100000 == 0:
                            print("[postcodes] Processed %s postcodes" % pcount)
                            print("[elasticsearch] %s postcodes to save" % len(postcodes))
                            results = bulk(es, postcodes)
                            print("[elasticsearch] saved %s postcodes to %s index" % (results[0], "geo_postcode"))
                            print("[elasticsearch] %s errors reported" % len(results[1]))
                            postcodes = []
                    print("[postcodes] Processed %s postcodes" % pcount)
                    print("[elasticsearch] %s postcodes to save" % len(postcodes))
                    results = bulk(es, postcodes)
                    print("[elasticsearch] saved %s postcodes to %s index" % (results[0], "geo_postcode"))
                    print("[elasticsearch] %s errors reported" % len(results[1]))
                    postcodes = []

            # add names and codes
            if not args.do_codes:
                continue 

            for j in code_files:
                if f.filename.startswith(j) and f.filename.endswith('.csv'):
                    codes = [i for i in NAME_FILES if i["file"] == j][0]
                    names_and_codes = []
                    print("[codes] adding codes for '%s' field" % codes["type_field"])
                    with pczip.open(f.filename, 'r') as nccsv:
                        nccsv = io.TextIOWrapper(nccsv, encoding='utf-8-sig')

                        # double tab delimiter in country codes causing issues
                        if codes["type_field"] == "ctry":
                            nccsv = (row.replace('\t\t', '\t') for row in nccsv)

                        reader = csv.DictReader(nccsv, delimiter=',')
                        field_names = None
                        for i in reader:
                            if not field_names:
                                field_names = {}
                                for n in reader.fieldnames:
                                    if n.endswith("CD"):
                                        field_names["code"] = n
                                    elif n.endswith("NM"):
                                        field_names["name"] = n
                                    elif n.endswith("NMW"):
                                        field_names["welsh_name"] = n
                                for k in ["name", "code", "welsh_name"]:
                                    if k not in field_names:
                                        field_names[k] = codes.get("{}_field".format(k))
                            i["_id"] = i[field_names["code"]]
                            i["_index"] = "geo_area"
                            i["_type"] = "_doc"
                            i["_op_type"] = "index"
                            i["type"] = codes["type_field"]
                            i["sort_order"] = i["_id"]
                            if codes["name_field"]:
                                i["name"] = i[field_names["name"]]
                                i["name_welsh"] = i["name"]
                                if field_names["welsh_name"]:
                                    i["name_welsh"] = i[field_names["welsh_name"]]

                            if '' in i:
                                del i['']
                            names_and_codes.append(i)
                        print("[elasticsearch] %s codes to save" % len(names_and_codes))
                        results = bulk(es, names_and_codes)
                        print("[elasticsearch] saved %s codes to %s index" % (results[0], "geo_area"))
                        print("[elasticsearch] %s errors reported" % len(results[1]))


if __name__ == '__main__':
    main()
