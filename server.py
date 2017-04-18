from __future__ import print_function
from datetime import datetime
import argparse
import math
from urllib.parse import urlencode

import bottle
from elasticsearch import Elasticsearch

from metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES
from controllers.postcodes import *
from controllers.areatypes import *
from controllers.areas import *
from controllers.points import *
from controllers.controller import *

app = bottle.default_app()

# @TODO delete
def get_area_search_link(q, p=1, size=100, filetype=None):
    query_vars = {"q": q}
    if p > 1:
        query_vars["page"] = p
    if size!=100:
        query_vars["size"] = size
    return "/areas/search{}?{}".format(set_url_filetype(filetype), urlencode(query_vars))

@app.route('/postcodes/redirect')
def postcode_redirect():
    postcode = bottle.request.query.postcode
    return bottle.redirect(get_postcode_link(postcode,"html"))

@app.route('/postcodes/<postcode>')
@app.route('/postcodes/<postcode>.<filetype>')
def postcode(postcode, filetype="json"):
    """ View details about a particular postcode
    """
    pc = Postcode(app.config)
    pc.get_by_id(postcode)
    return pc.return_result(filetype)

@app.route('/areas/search')
@app.route('/areas/search.<filetype>')
def areaname(filetype="json"):
    p = bottle.request.query.page or '1'
    p = int(p)
    size = bottle.request.query.size or '100'
    size = int(size)
    from_ = (p-1) * size
    areaname = bottle.request.query.q
    # @TODO order most important areas to top
    if areaname:
        result = app.config.get("es").search(index=app.config.get("es_index", "postcode"), doc_type='code', q=areaname, from_=from_, size=size, _source_exclude=["boundary"])
        areas = [{"id": a["_id"], "name": a["_source"]["name"], "type": a["_source"]["type"]} for a in result["hits"]["hits"]]
        pagination = {k:(get_area_search_link( areaname, v[0], v[1] ) if v else None) for k,v in get_pagination( p, size, result["hits"]["total"] ).items()}
        if filetype=="html":
            return bottle.template('areasearch.html',
                page=p, size=size, from_=from_,
                pagination=pagination,
                q=areaname,
                results=areas,
                result_count=result["hits"]["total"],
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
            )
        elif filetype=="json":
            links = pagination
            links["self"] = get_area_search_link( areaname, p, size )
            return {
                "data": [get_area_object(a) for a in result["hits"]["hits"]],
                "links": links,
                "meta": {
                    "total-results": result["hits"]["total"],
                    "query": areaname
                }
            }
    else:
        if filetype=="html":
            return bottle.template('areasearch.html'
            )
        elif filetype=="json":
            return {"result": []}

@app.route('/areas/<areacode>')
@app.route('/areas/<areacode>.<filetype>')
def area(areacode, filetype="json"):
    a = Area(app.config)
    if filetype=="geojson":
        a.get_by_id(areacode.strip(), boundary=True)
    else:
        a.get_by_id(areacode.strip())
    return a.return_result(filetype)

@app.route('/areatypes')
@app.route('/areatypes.<filetype>')
def areatypes_all(filetype="json"):
    ats = Areatypes( app.config )
    ats.get()
    return ats.return_result(filetype)

@app.route('/areatypes/<areatype>')
@app.route('/areatypes/<areatype>.<filetype>')
def areatype(areatype, filetype="json"):
    app.config["stop_recursion"] = False
    at = Areatype( app.config )
    at.get_by_id( areatype, int(bottle.request.query.page or '1'), int(bottle.request.query.size or '100') )
    return at.return_result(filetype)

@app.route('/points/<lat:float>,<lon:float>')
@app.route('/points/<lat:float>,<lon:float>.<filetype:re:(html|json)>')
def get_point(lat, lon, filetype="json"):
    po = Point( app.config )
    po.get_by_id( lat, lon )
    return po.return_result(filetype)

@app.route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root='./static')

def main():

    parser = argparse.ArgumentParser(description='') # @TODO fill in

    # server options
    parser.add_argument('-host', '--host', default="localhost", help='host for the server')
    parser.add_argument('-p', '--port', default=8080, help='port for the server')
    parser.add_argument('--debug', action='store_true', dest="debug", help='Debug mode (autoreloads the server)')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='postcode', help='index used to store postcode data')

    args = parser.parse_args()

    app.config["es"] = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)
    app.config["es_index"] = args.es_index

    bottle.run(app, host=args.host, port=args.port, reloader=args.debug)

if __name__ == '__main__':
    main()
