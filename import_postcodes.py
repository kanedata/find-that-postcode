import csv
import zipfile
import io
import argparse
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
    parser.add_argument('--es-index', default='postcode', help='index used to store postcode data')

    args = parser.parse_args()

    postcodes = []

    es = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)

    with zipfile.ZipFile(args.nspl) as pczip:
        for f in pczip.filelist:
            if f.filename.endswith(".csv") and f.filename.startswith("Data/multi_csv/NSPL_") and args.do_postcodes:
                print ("[postcodes] Opening %s" % f.filename)
                pcount = 0
                with pczip.open(f, 'rU') as pccsv:
                    pccsv  = io.TextIOWrapper(pccsv)
                    reader = csv.DictReader(pccsv)
                    for i in reader:
                        i["_index"] = args.es_index
                        i["_type"] = "postcode"
                        i["_op_type"] = "index"
                        i["_id"] = i["pcds"]

                        # null any blank fields
                        for k in i:
                            if i[k]=="":
                                i[k] = None

                        # date fields
                        for j in ["dointr", "doterm"]:
                            if i[j]:
                                i[j] = datetime.strptime(i[j], "%Y%m")

                        # latitude and longitude
                        for j in ["lat", "long"]:
                            if i[j]:
                                i[j] = float(i[j])
                                if i[j]==99.999999:
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
                            print("[elasticsearch] saved %s postcodes to %s index" % (results[0], args.es_index))
                            print("[elasticsearch] %s errors reported" % len(results[1]) )
                            postcodes = []
                    print("[postcodes] Processed %s postcodes" % pcount)
                    print("[elasticsearch] %s postcodes to save" % len(postcodes))
                    results = bulk(es, postcodes)
                    print("[elasticsearch] saved %s postcodes to %s index" % (results[0], args.es_index))
                    print("[elasticsearch] %s errors reported" % len(results[1]) )
                    postcodes = []

            # add names and codes
            if f.filename in [i["file"] for i in NAME_FILES] and args.do_codes:
                codes = [i for i in NAME_FILES if i["file"]==f.filename][0]
                names_and_codes = []
                print("[codes] adding codes for '%s' field" % codes["type_field"])
                with pczip.open(codes["file"], 'rU') as nccsv:
                    nccsv  = io.TextIOWrapper(nccsv)

                    # double tab delimiter in country codes causing issues
                    if codes["type_field"]=="ctry":
                        nccsv = (row.replace('\t\t', '\t') for row in nccsv)

                    reader = csv.DictReader(nccsv, delimiter='\t')
                    for i in reader:
                        i["_id"] = i[codes["code_field"]]
                        i["_index"] = args.es_index
                        i["_type"] = "code"
                        i["_op_type"] = "index"
                        i["type"] = codes["type_field"]
                        i["sort_order"] = i["_id"]
                        if codes["name_field"]:
                            i["name"] = i[codes["name_field"]]
                            i["name_welsh"] = i["name"]
                            if codes["welsh_name_field"]:
                                i["name_welsh"] = i[codes["welsh_name_field"]]

                        if '' in i:
                            del i['']
                        names_and_codes.append(i)
                    print("[elasticsearch] %s codes to save" % len(names_and_codes))
                    results = bulk(es, names_and_codes)
                    print("[elasticsearch] saved %s codes to %s index" % (results[0], args.es_index))
                    print("[elasticsearch] %s errors reported" % len(results[1]) )


if __name__ == '__main__':
    main()
