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

    return (filename, code_field)

def main():
    parser = argparse.ArgumentParser(description='Import area boundaries into elasticsearch.')

    # Postcode details
    parser.add_argument('boundary_files', type=str, nargs='+',
                        default='data/NSPL.zip',
                        help='URL or file path for each boundary file to import. Multiple URLs should be separated by a space')
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
        #(code, code_field, boundary_file) = parse_boundary_file(boundary_file)
        boundary_filename = "data/%s" % boundary_file.split('/')[-1]


        if not os.path.isfile(boundary_file ):
            if not os.path.isfile(boundary_filename):
                print("[%s] Downloading file" % (boundary_file))
                urllib.request.urlretrieve(boundary_file, boundary_filename)
            boundary_file = boundary_filename

        with open(boundary_file) as a:
            boundaries = json.load(a)
            errors = []

            if len(boundaries.get("features",[]))>0:
                test_boundary = boundaries.get("features",[])[0]
                code_fields = []
                for k in test_boundary.get("properties", {}):
                    if k.endswith("cd"):
                        code_fields.append(k)
                if len(code_fields)==1:
                    code_field = code_fields[0]
                elif len(code_fields)==0:
                    errors.append("[ERROR][%s] No code field found in file" % (boundary_file,))
                else:
                    errors.append("[ERROR][%s] Too many code fields found in file" % (boundary_file,))
            else:
                errors.append("[ERROR][%s] Features not found in file" % (boundary_file,))

            if len(errors)>0:
                if args.examine:
                    for e in errors:
                        print(e)
                else:
                    raise ValueError("; ".join(errors))

            code = code_field.replace("cd", "")

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
                print("[%s] Opened file: [%s]" % (code, boundary_file))
                bulk_boundaries = []
                errors = []
                boundaries_updated = 0
                for k, i in enumerate(boundaries["features"]):
                    boundary = {
                            "_index": args.es_index,
                            "_type": "code",
                            "_op_type": "update",
                            "_id": i["properties"][code_field],
                            "doc": {
                                "boundary": {
                                    "type": i["geometry"]["type"].lower(),
                                    "coordinates": i["geometry"]["coordinates"]
                                },
                                "has_boundary": True
                            }
                        }
                    bulk_boundaries.append(boundary)
                    results = es.update(index=args.es_index, doc_type="code", id=boundary["_id"], body={"doc": boundary["doc"]}, ignore=[404,400])
                    if results.get("error"):
                        e = "[%s] %s" % ( boundary["_id"], results.get("error",{}).get("reason", "Operation failed"))
                        errors.append(e)
                        print(e)
                    else:
                        boundaries_updated += 1
                        #print("[%s] Saved boundary" % boundary["_id"])
                print("[elasticsearch] %s boundaries saved" % boundaries_updated )
                print("[elasticsearch] %s errors reported" % len(errors) )
                # @TODO Log errors somewhere...


if __name__ == '__main__':
    main()
