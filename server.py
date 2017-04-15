from __future__ import print_function
from datetime import datetime
import argparse
import math

import bottle
from elasticsearch import Elasticsearch

from metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES

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

def get_pagination(url, current_page, page_size, total_results, range=5):
    pagination = {
        "next": None,
        "previous": None,
        "page_range": None,
        "start": None,
        "end": None
    }

    max_page = math.ceil(float(total_results) / float(page_size))

    # next page link
    if current_page < max_page:
        pagination["next"] = url % (current_page + 1)

    # previous page link
    if current_page > 1:
        pagination["previous"] = url % (current_page - 1)

    # start_page link
    if (current_page - 1) > 1:
        pagination["start"] = url % (1)

    # end page link
    if (current_page + 1) < max_page:
        pagination["end"] = url % (max_page)

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

def main():

    parser = argparse.ArgumentParser(description='Run a reconciliation service based on a CSV file')

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

    def process_postcode_result(postcode):
        for i in postcode:
            if postcode[i]:
                code = es.get(index=args.es_index, doc_type='code', id=postcode[i], ignore=[404], _source_exclude=["boundary"])#, _source_include=["name"])
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
                        "name": ""
                    }

        # sort out leps @TODO do this properly
        postcode["lep"] = postcode["lep1"]

        # turn dates into dates
        postcode["dointr"] = datetime.strptime(postcode["dointr"], "%Y-%m-%dT%H:%M:%S")
        if postcode["doterm"]:
            postcode["doterm"] = datetime.strptime(postcode["doterm"], "%Y-%m-%dT%H:%M:%S")

        return postcode

    @bottle.route('/postcode/redirect')
    def postcode_redirect():
        postcode = bottle.request.query.postcode
        return bottle.redirect('/postcode/%s.html' % postcode)

    @bottle.route('/postcode/<postcode>')
    @bottle.route('/postcode/<postcode>.<filetype>')
    def postcode(postcode, filetype="json"):
        """ View details about a particular postcode
        """
        postcode = postcode.replace("+", "")
        postcode = parse_postcode(postcode)
        result = es.get(index=args.es_index, doc_type='postcode', id=postcode, ignore=[404])
        if result["found"]:

            if filetype=="html":
                result["_source"] = process_postcode_result(result["_source"])

                return bottle.template('postcode.html',
                    result=result["_source"],
                    postcode=result["_id"],
                    point=None,
                    area_types=AREA_TYPES,
                    key_area_types=KEY_AREA_TYPES,
                    other_codes=OTHER_CODES
                    )
            elif filetype=="json":
                return result["_source"]



    @bottle.route('/area/search')
    @bottle.route('/area/search.<filetype>')
    def areaname(filetype="json"):
        p = bottle.request.query.p or '1'
        p = int(p)
        size = bottle.request.query.size or '100'
        size = int(size)
        from_ = (p-1) * size
        areaname = bottle.request.query.q
        # @TODO order most important areas to top
        if areaname:
            result = es.search(index=args.es_index, doc_type='code', q=areaname, from_=from_, size=size, _source_exclude=["boundary"])
            areas = [{"id": a["_id"], "name": a["_source"]["name"], "type": a["_source"]["type"]} for a in result["hits"]["hits"]]
            if filetype=="html":
                return bottle.template('areasearch.html',
                page=p, size=size, from_=from_,
                pagination=get_pagination( '/area/search.html?q=%s&p=%%s' % areaname, p, size, result["hits"]["total"] ),
                q=areaname,
                results=areas,
                result_count=result["hits"]["total"],
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
            elif filetype=="json":
                return {"result": areas}
        else:
            if filetype=="html":
                return bottle.template('areasearch.html'
                )
            elif filetype=="json":
                return {"result": []}

    @bottle.route('/area/<areacode>')
    @bottle.route('/area/<areacode>.<filetype>')
    def area(areacode, filetype="json"):
        _source_exclude = ["boundary"]
        if filetype=="geojson":
            _source_exclude = []

        result = es.get(index=args.es_index, doc_type='code', id=areacode, ignore=[404], _source_exclude=_source_exclude)
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
                example = es.search(index=args.es_index, doc_type='postcode', body=query, size=5)
                result["_source"]["examples"] = [{"postcode": e["_id"], "location": e["_source"]["location"]} for e in example["hits"]["hits"]]
            area_type=[a for a in AREA_TYPES if a[0]==result["_source"]["type"]][0]
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
                return result["_source"]
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

    @bottle.route('/areatype')
    @bottle.route('/areatype.<filetype>')
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
        result = es.search(index=args.es_index, doc_type='code', body=query, _source_exclude=["boundary"])
        area_counts = {i["key"]:i["doc_count"] for i in result["aggregations"]["group_by_type"]["buckets"]}


        if filetype=="html":
            return bottle.template('areatypes.html',
                area_counts=area_counts,
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        else:
            return {"result": AREA_TYPES}

    @bottle.route('/areatype/<areatype>')
    @bottle.route('/areatype/<areatype>.<filetype>')
    def areatype(areatype, filetype="json"):
        p = bottle.request.query.p or '1'
        p = int(p)
        size = bottle.request.query.size or '100'
        size = int(size)
        from_ = (p-1) * size
        # @TODO paging of results
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
        result = es.search(index=args.es_index, doc_type='code', body=query, from_=from_, size=size, _source_exclude=["boundary"])
        if filetype=="html":
            return bottle.template('areatype.html',
                result=result["hits"]["hits"],
                count_areas = result["hits"]["total"],
                page=p, size=size, from_=from_,
                pagination=get_pagination( '/areatype/%s.html?p=%%s' % areatype, p, size, result["hits"]["total"] ),
                area_type=[a for a in AREA_TYPES if a[0]==areatype][0],
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return {"result": result["hits"]["hits"]}

    @bottle.route('/point/<lat:float>,<lon:float>')
    @bottle.route('/point/<lat:float>,<lon:float>.<filetype>')
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
        result = es.search(index=args.es_index, doc_type='postcode', body=query, size=1)
        postcode = result["hits"]["hits"][0]

        if postcode["sort"][0]>10000:

            if filetype=="html":
                postcode["_source"] = process_postcode_result(postcode["_source"])

                return bottle.template('point_error.html',
                    postcode=postcode["_id"],
                    point={"lat": lat, "lon": lon, "distance": postcode["sort"][0]}
                    )
            elif filetype=="json":
                return {"result": "Nearest postcode is more than 10km away. Are you sure this point is in the UK?"}

        if filetype=="html":
            postcode["_source"] = process_postcode_result(postcode["_source"])

            return bottle.template('postcode.html',
                result=postcode["_source"],
                postcode=postcode["_id"],
                point={"lat": lat, "lon": lon, "distance": postcode["sort"][0]},
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return postcode["_source"]

    @bottle.route('/static/<filename:path>')
    def send_static(filename):
        """ if we need static files
        """
        return bottle.static_file(filename, root='./static')

    bottle.run(host=args.host, port=args.port, reloader=args.debug)

if __name__ == '__main__':
    main()
