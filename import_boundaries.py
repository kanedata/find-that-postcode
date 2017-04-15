import csv
import urllib.request
import argparse
from datetime import datetime
import os
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from metadata import NAME_FILES

def parse_boundary_file(boundary_file):

    reader = csv.reader([boundary_file], delimiter=':', quotechar="'")
    boundary_file = next(reader)

    if len(boundary_file)==2:
        code = boundary_file[0]
        code_field = None
        filename = boundary_file[1]
    elif len(boundary_file)==3:
        code = boundary_file[0]
        filename = boundary_file[1]
        code_field = boundary_file[2]
    else:
        raise ValueError("Could not parse boundary file")


    if not code_field:
        codes = [i["code_field"] for i in NAME_FILES if i["type_field"]==code]
        if len(codes)>0:
            code_field = codes[0].lower()
        else:
            raise ValueError("Could not determine code field")

    return (code, code_field, filename)

def main():
    parser = argparse.ArgumentParser(description='Import area boundaries into elasticsearch.')

    # Postcode details
    parser.add_argument('boundary_files', type=str, nargs='+',
                        default='data/NSPL.zip',
                        help='Entry for each boundary file to import. In format `code:url` or `code:url:code_field`. `url` can be a local path or a remote URL. URL should be in quotes (\' not double-quotes) if it contains a colon :.')
    parser.add_argument('--examine', action='store_true', help="Give info about the shape of the file, don't execute the import")

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='postcode', help='index used to store postcode data')

    args = parser.parse_args()

    boundaries = []

    es = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)

    for boundary_file in args.boundary_files:
        (code, code_field, boundary_file) = parse_boundary_file(boundary_file)


        if not os.path.isfile(boundary_file ):
            urllib.request.urlretrieve(boundary_file, "data/%s_boundary.geojson" % code)
            boundary_file = "data/%s_boundary.geojson" % code

        with open(boundary_file) as a:
            boundaries = json.load(a)

            if args.examine:
                print("[%s] Opened file: [%s]" % (code, boundary_file))
                print("[%s] Looking for code field: [%s]" % (code, code_field))
                print("[%s] Geojson type: [%s]" % (code, boundaries["type"]))
                print("[%s] Number of features [%s]" % (code, len(boundaries["features"])))
                for k, i in enumerate(boundaries["features"][:5]):
                    print("[%s] Feature %s type %s" % (code, k, i["type"]))
                    print("[%s] Feature %s properties %s" % (code, k, list(i["properties"].keys())))
                    print("[%s] Feature %s geometry type %s" % (code, k, i["geometry"]["type"]))
                    print("[%s] Feature %s geometry length %s" % (code, k, len(str(i["geometry"]["coordinates"]))) )
                    if code_field in i["properties"]:
                        print("[%s] Feature %s Code %s" % (code, k, i["properties"][code_field]))
                    else:
                        print("[ERROR][%s] Feature %s Code field not found" % (code, k,))

            else:
                bulk_boundaries = []
                for k, i in enumerate(boundaries["features"]):
                    bulk_boundaries.append({
                            "_index": args.es_index,
                            "_type": "code",
                            "_op_type": "update",
                            "_id": i["properties"][code_field],
                            "doc": {
                                "boundary": {
                                    "type": i["geometry"]["type"].lower(),
                                    "coordinates": i["geometry"]["coordinates"]
                                }
                            }
                        })
                print("[elasticsearch] %s boundaries to save" % len(bulk_boundaries))
                results = bulk(es, bulk_boundaries)
                print("[elasticsearch] saved %s boundaries to %s index" % (results[0], args.es_index))
                print("[elasticsearch] %s errors reported" % len(results[1]) )


if __name__ == '__main__':
    main()
