from __future__ import print_function
from datetime import datetime
import argparse
import math
from urllib.parse import urlencode

import bottle
from elasticsearch import Elasticsearch

from metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES
from controllers import postcodes, areatypes

app = bottle.default_app()

# @TODO delete
def set_url_filetype(filetype=None):
    if filetype:
        return "." + filetype
    return ""

# @TODO delete
def get_area_type(areatype):
    possible_types = [a for a in AREA_TYPES if a[0]==areatype]
    if len(possible_types)==1:
        return possible_types[0]
    return []


def get_area_search_link(q, p=1, size=100, filetype=None):
    query_vars = {"q": q}
    if p > 1:
        query_vars["page"] = p
    if size!=100:
        query_vars["size"] = size
    return "/areas/search{}?{}".format(set_url_filetype(filetype), urlencode(query_vars))

def get_areatype_link(areatypeid, p=1, size=100, filetype=None):
    query_vars = {}
    if p > 1:
        query_vars["page"] = p
    if size!=100:
        query_vars["size"] = size
    if len(query_vars)>0:
        return "/areatypes/{}{}?{}".format(areatypeid, set_url_filetype(filetype), urlencode(query_vars))
    else:
        return "/areatypes/{}{}".format(areatypeid, set_url_filetype(filetype))

def get_point_link(lat, lon, filetype=None):
    return "/points/{},{}{}".format(lat, lon, set_url_filetype(filetype))

@app.route('/postcodes/redirect')
def postcode_redirect():
    postcode = bottle.request.query.postcode
    return bottle.redirect(get_postcode_link(postcode,"html"))

@app.route('/postcodes/<postcode>')
@app.route('/postcodes/<postcode>.<filetype>')
def postcode(postcode, filetype="json"):
    """ View details about a particular postcode
    """
    pc = postcodes.Postcode(app.config.get("es"), app.config.get("es_index", "postcode"))
    pc.get(postcode)
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
    _source_exclude = ["boundary"]
    if filetype=="geojson":
        _source_exclude = []

    result = app.config.get("es").get(index=app.config.get("es_index", "postcode"), doc_type='code', id=areacode, ignore=[404], _source_exclude=_source_exclude)
    if result["found"]:
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "query_string": {
                            "query": areacode
                        }
                    },
                    "random_score": {}
                }

            }
        }
        if filetype!="geojson":
            example = app.config.get("es").search(index=app.config.get("es_index", "postcode"), doc_type='postcode', body=query, size=5)
            result["_source"]["examples"] = [{"postcode": e["_id"], "location": e["_source"].get("location", {})} for e in example["hits"]["hits"]]
        area_type=get_area_type(result["_source"]["type"])
        result["_source"]["type_name"] = area_type[1]

        if filetype=="html":
            return bottle.template('area.html',
                result=result["_source"],
                area=areacode,
                area_type=area_type,
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return {
                "data": get_area_object(result),
                "links": {
                    "self": get_area_link( areacode ),
                    "geojson": get_area_link( areacode, filetype="geojson" ) # @TODO need to check whether boundary data actually exists before applying this
                }
            }
        elif filetype=="geojson":
            if "boundary" not in result["_source"]:
                bottle.abort(404, "boundary not found")
            return {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": GEOJSON_TYPES[result["_source"]["boundary"]["type"]],
                            "coordinates": result["_source"]["boundary"]["coordinates"]
                        },
                        "properties": {k:v for k,v in result["_source"].items() if k!="boundary"}
                    }
                ]
            }

@app.route('/areatypes')
@app.route('/areatypes.<filetype>')
def areatypes_all(filetype="json"):

    query = {
    	"size": 0,
    	"aggs": {
    		"group_by_type": {
    			"terms": {
    				"field": "type.keyword",
    				"size": 100
    			}
    		}
    	}
    }
    result = app.config.get("es").search(index=app.config.get("es_index", "postcode"), doc_type='code', body=query, _source_exclude=["boundary"])
    area_counts = {i["key"]:i["doc_count"] for i in result["aggregations"]["group_by_type"]["buckets"]}
    if filetype=="html":
        return bottle.template('areatypes.html',
            area_counts=area_counts,
            area_types=AREA_TYPES,
            key_area_types=KEY_AREA_TYPES,
            other_codes=OTHER_CODES
            )
    else:
        return {
            "data": [get_areatype_object(a, area_counts.get(a[0], None)) for a in AREA_TYPES],
            "links": {"self": "/areatypes"}
        }

@app.route('/areatypes/<areatype>')
@app.route('/areatypes/<areatype>.<filetype>')
def areatype(areatype, filetype="json"):
    at = areatypes.Areatype( app.config.get("es"), app.config.get("es_index", "postcode"))
    at.get( areatype, int(bottle.request.query.page or '1'), int(bottle.request.query.size or '100') )
    return at.return_result(filetype)

@app.route('/points/<lat:float>,<lon:float>')
@app.route('/points/<lat:float>,<lon:float>.<filetype>')
def get_point(lat, lon, filetype="json"):
    query = {
    	"query": {
    		"match_all": {}
    	},
    	"sort": [
    		{
    			"_geo_distance": {
    				"location": {
    					"lat": lat,
    					"lon": lon
    				},
    				"unit": "m"
    			}
    		}
    	]
    }
    result = app.config.get("es").search(index=app.config.get("es_index", "postcode"), doc_type='postcode', body=query, size=1)
    postcode = result["hits"]["hits"][0]

    if postcode["sort"][0]>10000:

        if filetype=="html":
            postcode["_source"] = process_postcode_result(postcode["_source"], app.config.get("es"), app.config.get("es_index", "postcode"))

            return bottle.template('point_error.html',
                postcode=postcode["_id"],
                point={"lat": lat, "lon": lon, "distance": postcode["sort"][0]}
                )
        elif filetype=="json":
            return bottle.HTTPResponse({
                "errors": [{
                    "status": "400",
                    "code": "point_outside_uk",
                    "title": "Nearest postcode ({}) is more than 10km away ({:,.1f}km). Are you sure this point is in the UK?".format( postcode["_id"], (postcode["sort"][0] / 1000) )
                }]
            }, status=400)

    postcode["_source"] = process_postcode_result(postcode["_source"], app.config.get("es"), app.config.get("es_index", "postcode"))
    if filetype=="html":

        return bottle.template('postcode.html',
            result=postcode["_source"],
            postcode=postcode["_id"],
            point={"lat": lat, "lon": lon, "distance": postcode["sort"][0]},
            area_types=AREA_TYPES,
            key_area_types=KEY_AREA_TYPES,
            other_codes=OTHER_CODES
            )
    elif filetype=="json":
        return {
            "included": get_postcode_included(postcode),
            "data": {
                "type": "points",
                "id": "%s,%s" % (lat,lon),
                "attributes": {
                    "latitude": lat,
                    "longitude": lon,
                    "distance_from_postcode": postcode["sort"][0]
                },
                "relationships": {
                    "nearest_postcode": {
                        "data": get_postcode_object(postcode),
                        "links": {
                            "self": "/points/{},{}/relationships/nearest_postcode".format(lat,lon),
                            "related": "/points/{},{}/nearest_postcode".format(lat,lon),
                        }
                    }
                }
            },
            "links": { "self": get_point_link(lat,lon) },
        }

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

    es = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)
    app.config["es"] = es
    app.config["es_index"] = args.es_index

    bottle.run(app, host=args.host, port=args.port, reloader=args.debug)

if __name__ == '__main__':
    main()
