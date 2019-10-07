from __future__ import print_function
import csv
import argparse
import sys
from elasticsearch import Elasticsearch
from controllers.postcodes import Postcode

# List of potential postcode fields
POSTCODE_FIELDS = ["postcode", "postal_code", "post_code", "post code"]


def process_csv(csvfile, outfile, config,
                postcode_field="postcode",
                fields=["lat", "long", "cty"]):

    # @TODO add option for different CSV dialects and for no headers
    # In the case of no headers you would find the field by number
    reader = csv.DictReader(csvfile)
    writer = csv.DictWriter(outfile, reader.fieldnames + fields)
    writer.writeheader()
    code_cache = {
        "E99999999": "",
        "S99999999": "",
        "N99999999": "",
        "W99999999": ""
    }
    for _, row in enumerate(reader):
        for i in fields:
            row[i] = None
        postcode = Postcode.parse_postcode(row.get(postcode_field))
        if postcode:
            pc = config.get("es").get(index=config.get("es_index"), doc_type="postcode", id=postcode, ignore=[404])
            if pc["found"]:
                for i in fields:
                    if i.endswith("_name"):
                        code = pc["_source"].get(i[:-5])
                        if code in code_cache:
                            row[i] = code_cache[code]
                        elif code:
                            area = config.get("es").get(index=config.get("es_index"), doc_type="code", id=code, ignore=[404], _source_exclude=["boundary"])
                            if area["found"]:
                                row[i] = area["_source"].get("name")
                            else:
                                row[i] = code
                            code_cache[code] = row[i]
                        else:
                            row[i] = code
                    else:
                        row[i] = pc["_source"].get(i)
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description='Process a CSV file, adding details about each postcode found.')

    # fields to be included
    parser.add_argument('--fields', default="lat,long,cty", help='Comma-separated list of fields that will be added to the returned CSV')
    parser.add_argument('--postcode-field', default="postcode", help="title of the field holding the postcode")

    # files
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help="Source CSV file")
    parser.add_argument('outfile', nargs='?', default=None, help="CSV file to output")

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='postcode', help='index used to store postcode data')

    # @TODO add CSV dialect options

    args = parser.parse_args()

    config = {
        "es": Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl),
        "es_index": args.es_index
    }
    args.fields = [f.strip() for f in args.fields.split(",")]

    if args.outfile:
        with open(args.outfile, 'w', newline='') as outfile:
            process_csv(args.infile, outfile, config, args.postcode_field, args.fields)
    else:
        process_csv(args.infile, sys.stdout, config, args.postcode_field, args.fields)

if __name__ == '__main__':
    main()
