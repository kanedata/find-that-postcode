import argparse
from elasticsearch import Elasticsearch
import os


INDEXES = {
    "geo_postcode": {
        "properties": {
            "location": {"type": "geo_point"}
        }
    },
    "geo_placename": {
        "properties": {
            "location": {"type": "geo_point"}
        }
    },
    "geo_area": {
        "properties": {
            "boundary": {"type": "geo_shape"}
        }
    }
}


def main():

    parser = argparse.ArgumentParser(description='Setup elasticsearch indexes.')
    parser.add_argument('--reset', action='store_true',
                        help='If set, any existing indexes will be deleted and recreated.')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost",
                        help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200,
                        help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='',
                        help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true',
                        help='Use ssl to connect to elasticsearch')

    args = parser.parse_args()

    es = Elasticsearch(host=args.es_host, port=args.es_port,
                       url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)

    potential_env_vars = [
        "ELASTICSEARCH_URL",
        "ES_URL",
        "BONSAI_URL"
    ]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            es = Elasticsearch(os.environ.get(e_v))
            break

    for index, i in INDEXES.items():
        if es.indices.exists(index) and args.reset:
            print("[elasticsearch] deleting '%s' index..." % (index))
            res = es.indices.delete(index=index)
            print("[elasticsearch] response: '%s'" % (res))
        print("[elasticsearch] creating '%s' index..." % (index))
        res = es.indices.create(index=index)
        res = es.indices.put_mapping(doc_type='_doc', body=i, index=index)
        print("[elasticsearch] set mapping on %s index" % (index))

if __name__ == '__main__':
    main()
