from __future__ import print_function
from datetime import datetime
import argparse
import math
from urllib.parse import urlencode

import bottle
from elasticsearch import Elasticsearch

from metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES

app = bottle.default_app()

def parse_postcode(postcode):
    """
    standardises a postcode into the correct format
    """

    if postcode is None:
        return None

    # check for blank/empty
    postcode = postcode.strip()
    if postcode=='':
        return None

    # check for nonstandard codes
    if len(postcode.replace(" ", ""))>7:
        return postcode

    first_part = postcode[:-3].strip()
    last_part = postcode[-3:].strip()

    # check for incorrect characters
    first_part = list(first_part)
    last_part = list(last_part)
    if last_part[0]=="O":
        last_part[0] = "0"

    return "%s %s" % ("".join(first_part), "".join(last_part) )

def get_pagination(current_page, page_size, total_results, range=5):
    pagination = {
        "next": None,
        "prev": None,
        #"page_range": None,
        "first": None,
        "last": None
    }

    max_page = math.ceil(float(total_results) / float(page_size))

    # next page link
    if current_page < max_page:
        pagination["next"] = (current_page + 1, page_size)

    # previous page link
    if current_page > 1:
        pagination["prev"] = (current_page - 1, page_size)

    # start_page link
    if (current_page - 1) > 1:
        pagination["first"] = (1, page_size)

    # end page link
    if (current_page + 1) < max_page:
        pagination["last"] = (max_page, page_size)

    # page ranges
    # @TODO calculate page ranges

    return pagination

GEOJSON_TYPES = {
    "point": "Point", # A single geographic coordinate.
    "linestring": "LineString", # An arbitrary line given two or more points.
    "polygon": "Polygon", # A closed polygon whose first and last point must match, thus requiring n + 1 vertices to create an n-sided polygon and a minimum of 4 vertices.
    "multipoint": "MultiPoint", # An array of unconnected, but likely related points.
    "multilinestring": "MultiLineString", # An array of separate linestrings.
    "multipolygon": "MultiPolygon", # An array of separate polygons.
    "geometrycollection": "GeometryCollection", # A GeoJSON shape similar to the multi* shapes except that multiple types can coexist (e.g., a Point and a LineString).
}


def process_postcode_result(postcode, es, es_index):
    for i in postcode:
        if postcode[i]:
            code = es.get(index=es_index, doc_type='code', id=postcode[i], ignore=[404], _source_exclude=["boundary"])#, _source_include=["name"])
            if i in ["osgrdind", "usertype"]:
                pass
            elif code["found"]:
                code["_source"]["id"] = code["_id"]
                postcode[i] = code["_source"]
                if code["_id"].endswith("99999999"):
                    postcode[i]["name"] = ""
            elif i in ["wz11", "oa11"]:
                postcode[i] = {
                    "id": postcode[i],
                    "name": "",
                    "type": i,
                    "typename":  get_area_type(i)[2]
                }

    # sort out leps @TODO do this properly
    postcode["lep"] = postcode["lep1"]

    # turn dates into dates
    postcode["dointr"] = datetime.strptime(postcode["dointr"], "%Y-%m-%dT%H:%M:%S")
    if postcode["doterm"]:
        postcode["doterm"] = datetime.strptime(postcode["doterm"], "%Y-%m-%dT%H:%M:%S")

    return postcode

def set_url_filetype(filetype=None):
    if filetype:
        return "." + filetype
    return ""

def get_area_type(areatype):
    possible_types = [a for a in AREA_TYPES if a[0]==areatype]
    if len(possible_types)==1:
        return possible_types[0]
    return []

def get_area_object(area):
    return {
        "type": "areas",
        "id": area["_id"],
        "attributes": {
            "name": area["_source"]["name"],
            "name_welsh": area["_source"].get("name_welsh"),
            "type": area["_source"]["type"],
            "typename": get_area_type(area["_source"]["type"])[2]
        },
        "relationships": {
            "links": {
                "self": get_area_link(area["_id"]),
                "related": get_areatype_link(area["_source"]["type"])
            }
        }
    }

def get_area_link(areaid, filetype=None):
    return "/areas/{}{}".format(areaid, set_url_filetype(filetype))

def get_area_search_link(q, p=1, size=100, filetype=None):
    query_vars = {"q": q}
    if p > 1:
        query_vars["page"] = p
    if size!=100:
        query_vars["size"] = size
    return "/areas/search{}?{}".format(set_url_filetype(filetype), urlencode(query_vars))

def get_areatype_object(areatype, count_areas= None):
    return {
        "type": "areatypes",
        "id": areatype[0],
        "attributes": {
            "name": areatype[1],
            "name_full": areatype[2],
            "description": areatype[3],
            "count": count_areas
        },
        "relationships": {
            "links": {
                "self": get_areatype_link(areatype[0])
            }
        }
    }

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

def get_postcode_object(postcode):
    for i in ["dointr", "doterm"]:
        if postcode["_source"][i]:
            postcode["_source"][i] = postcode["_source"][i].strftime("%Y%m")
    attributes = {}
    for i in postcode["_source"]:
        if not isinstance(postcode["_source"][i], dict):
            attributes[i] = postcode["_source"][i]
        elif "id" not in postcode["_source"][i]:
            attributes[i] = postcode["_source"][i]
    return {
        "type": "postcodes",
        "id": postcode["_id"],
        "attributes": attributes,
        "relationships": {
            "areas": {
                "data": [{
                    "type": "areas",
                    "id": postcode["_source"][a[0]]["id"]
                } for a in AREA_TYPES if a[0] in postcode["_source"]],
                "links": {
                    "self": "/postcodes/{}/relationships/areas".format(postcode["_id"]),
                    "related": "/postcodes/{}/areas".format(postcode["_id"])
                }
            }
        }
    }

def get_postcode_included(postcode):
    areas = [postcode["_source"][a[0]] for a in AREA_TYPES if a[0] in postcode["_source"]]
    return [get_area_object({
        "_id": a["id"],
        "_source": a
    }) for a in areas]

def get_postcode_link(postcode, filetype=None):
    return "/postcodes/{}{}".format(postcode, set_url_filetype(filetype))

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
    postcode = postcode.replace("+", "")
    postcode = parse_postcode(postcode)
    result = app.config.get("es").get(index=app.config.get("es_index", "postcode"), doc_type='postcode', id=postcode, ignore=[404])
    if result["found"]:
        result["_source"] = process_postcode_result(result["_source"], app.config.get("es"), app.config.get("es_index", "postcode"))

        if filetype=="html":

            return bottle.template('postcode.html',
                result=result["_source"],
                postcode=result["_id"],
                point=None,
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return {
                "included": get_postcode_included(result),
                "data": get_postcode_object(result),
                "links": {"self": get_postcode_link(result["_id"])}
            }



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
                "links": {"self": get_area_link( areacode )}
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
def areatypes(filetype="json"):

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
    p = bottle.request.query.page or '1'
    p = int(p)
    size = bottle.request.query.size or '100'
    size = int(size)
    from_ = (p-1) * size
    query = {
        "query": {
            "match": {
                "type": areatype
            }
        },
        "sort": [
            {"sort_order.keyword": "asc" } # @TODO sort by _id? ??
        ]
    }
    result = app.config.get("es").search(index=app.config.get("es_index", "postcode"), doc_type='code', body=query, from_=from_, size=size, _source_exclude=["boundary"])
    area_type = get_area_type(areatype)
    pagination = {k:(get_areatype_link(areatype, v[0], v[1]) if v else None) for k,v in get_pagination( p, size, result["hits"]["total"] ).items()}
    if filetype=="html":
        return bottle.template('areatype.html',
            result=result["hits"]["hits"],
            count_areas = result["hits"]["total"],
            page=p, size=size, from_=from_,
            pagination=pagination,
            area_type=area_type,
            area_types=AREA_TYPES,
            key_area_types=KEY_AREA_TYPES,
            other_codes=OTHER_CODES
            )
    elif filetype=="json":
        areatype_json = get_areatype_object(area_type, count_areas=result["hits"]["total"])
        areatype_json["relationships"] = {
            "areas": {
                "data": [{
                    "type": "areas",
                    "id": a["_id"]
                } for a in result["hits"]["hits"]],
                "links": {
                    "self": "/areatypes/{}/relationships/areas".format(area_type[0]),
                    "related": "/areatypes/{}/areas".format(area_type[0])
                }
            }
        }
        links = pagination
        links["self"] = get_areatype_link(areatype, p, size)
        return {
            "data": areatype_json,
            "links": links,
            "included": [get_area_object(a) for a in result["hits"]["hits"]]
        }

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
    """ if we need static files
    """
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
