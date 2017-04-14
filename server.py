from __future__ import print_function
import bottle
from elasticsearch import Elasticsearch
from datetime import datetime

GMAPS_API_KEY = '' # @TODO move to config
AREA_TYPES = [
    ("oa11", "Output area", "2011 Census Output Area (OA)/ Small Area (SA)", "The 2011 Census OAs in GB and SAs in Northern Ireland were based on 2001 Census OAs, and they form the building bricks for defining higher level geographies. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no grid reference."),
    ("cty", "County", "County", "The current county to which the postcode has been assigned. Pseudo codes are included for English UAs, Wales, Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("laua", "Local Authority", "Local Authority District (LAD)/unitary authority (UA)/metropolitan district (MD)/London borough (LB)/ council area (CA)/district council area (DCA)", "The current district/UA to which the postcode has been assigned. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("ward", "Ward", "(Electoral) ward/division", "The current administrative/electoral area to which the postcode has been assigned. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("hlthau", "Strategic Health Authority", "Former Strategic Health Authority (SHA)/ Local Health Board (LHB)/ Health Board (HB)/ Health Authority (HA)/ Health & Social Care Board (HSCB)", "The health area code for the postcode. SHAs were abolished in England in 2013 but the codes remain as a 'frozen' geography. The field will otherwise be blank for postcodes with no OA code."),
    ("hro", "Pan SHA", "Pan SHA", "The Pan SHA responsible for the associated strategic health authority for each postcode in England. Pseudo codes are included for Wales, Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("ctry", "Country", "Country", "The code for the appropriate country (i.e. one of the four constituent countries of the UK or Crown dependencies - the Channel Islands or the Isle of Man) to which each postcode is assigned."),
    ("gor", "Region", "Region (former GOR)", "The region code for each postcode. Pseudo codes are included for Wales, Scotland, Northern Ireland, Channel Island and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("pcon", "Westminster parliamentary constituency", "Westminster parliamentary constituency", "The Westminster parliamentary constituency code for each postcode. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("eer", "European Electoral Region", "European Electoral Region (EER)", "The European Electoral Region code for each postcode. A pseudo code is included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code"),
    ("teclec", "Local Learning and Skills Council", "Local Learning and Skills Council (LLSC)/ Dept. of Children, Education, Lifelong Learning and Skills (DCELLS)/Enterprise Region (ER)", "The LLSC (England), DCELLS (Wales) or ER (Scotland) code for each postcode. Pseudo codes are included for Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("ttwa", "Travel to Work Area (TTWA)", "Travel to Work Area", "The TTWA code for the postcode. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("pct", "Primary Care Trust", "Primary Care Trust (PCT)/ Care Trust/Care Trust Plus (CT)/ Local Health Board (LHB)/Community Health Partnership (CHP)/ Local Commissioning Group (LCG)/Primary Healthcare Directorate (PHD)", "The code for the PCT/CT areas in England, LHBs in Wales, CHPs in Scotland, LCG in Northern Ireland and PHD in the Isle of Man. A pseudo code is included for Channel Islands. The field will otherwise be blank for postcodes with no OA code."),
    ("nuts", "LAU2 area", "LAU2 area", "The national LAU2-equivalent code for each postcode. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no grid reference"),
    ("park", "National park", "National park", "The National parks cover parts of England, Wales and Scotland. Pseudo codes are included for Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no grid reference."),
    ("lsoa11", "Lower Super Output Area", "2011 Census Lower Layer Super Output Area (LSOA)/ Data Zone (DZ)/ SOA", "The 2011 Census LSOA code for England and Wales, SOA code for Northern Ireland and DZ code for Scotland. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code. N.B. NI SOAs remain unchanged from 2001."),
    ("msoa11", "Middle Super Output Area", "Middle Layer Super Output Area (MSOA)/Intermediate Zone (IZ)", "The 2011 Census MSOA code for England and Wales and IZ code for Scotland. Pseudo codes are included for Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("wz11", "Workplace Zone", "2011 Census Workplace Zone", "The UK WZ code. Pseudo codes are included for Channel Islands and Isle of Man. The field will be blank for UK postcodes with no grid reference."),
    ("ccg", "Clinical Commissioning Group", "Clinical Commissioning Group (CCG)/Local Health Board (LHB)/Community Health Partnership (CHP)/ Local Commissioning Group (LCG)/Primary Healthcare Directorate (PHD)", "The code for the CCG areas in England, LHBs in Wales, CHPs in Scotland, LCG in Northern Ireland and PHD in the Isle of Man. A pseudo code is included for Channel Islands. The field will be blank for postcodes in England or Wales with no OA code."),
    ("bua11", "Built-up Area", "Built-up Area (BUA)", "The code for the BUAs in England and Wales. Pseudo codes are included for those OAs not classed as 'built-up' and cross-border codes are included for areas straddling the English/Welsh border. Pseudo codes are also included for Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("buasd11", "Built-up Area Sub-division (BUASD)", "Built-up Area Sub-division", "The code for the BUASDs in England and Wales. Pseudo codes are included for those OAs not classed as 'built-up' and cross-border codes are included for areas straddling the English/Welsh border. Pseudo codes are also included for Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code"),
    ("ru11ind", "Rural/Urban Classification", "2011 Census rural-urban classification", "The 2011 Census rural-urban classification of OAs for England and Wales, Scotland and Northern Ireland. A pseudo code is included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("oac11", "Output Area Classification", "2011 Census Output Area classification (OAC)", "The 2011 Census OAC code for each postcode in the UK. A pseudo code is included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code"),
    ("lep", "Local Enterprise Partnership", "Local Enterprise Partnership (LEP)", "The primary LEP code for each English postcode. Pseudo codes are included for the rest of the UK. The field will otherwise be blank for postcodes with no OA code."),
    ("pfa", "Police Force Area", "Police Force Area (PFA)", "The PFA code for each postcode. A single PFA covers each of Scotland and Northern Ireland (not coded). A pseudo code is included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
]

KEY_AREA_TYPES = [
    ("Key", ["ctry", "region", "cty", "laua", "ward", "oa11", "pcon"]),
    ("Secondary", ["ttwa", "pfa", "lep", "msoa11", "lsoa11", "park"]),
    ("Health", ["ccg", "hlthau", "hro", "pct"]),
    ("Other", ["eer", "bua11", "buasd11", "wz11", "teclec", "nuts"]),
]

OTHER_CODES = {
    "osgrdind": [
        "", # no code 0
        "within the building of the matched address closest to the postcode mean",
        "as for status value 1, except by visual inspection of Landline maps (Scotland only)",
        "approximate to within 50 metres",
        "postcode unit mean (mean of matched addresses with the same postcode, but not snapped to a building)",
        "imputed by ONS, by reference to surrounding postcode grid references",
        "postcode sector mean, (mainly PO Boxes)",
        "", # code 7 missing
        "postcode terminated prior to Gridlink(R) initiative, last known ONS postcode grid reference",
        "no grid reference available",
    ],
    "usertype": ["Small user", "Large user"],
    "imd": {
        "E92000001": 32844,
        "W92000004": 1909,
        "S92000003": 6976,
        "N92000002": None,
        "L93000001": None,
        "M83000003": None
    }
}

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

es = Elasticsearch()

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
    result = es.get(index='postcode', doc_type='postcode', id=postcode, ignore=[404])
    if result["found"]:

        if filetype=="html":
            result["_source"] = process_postcode_result(result["_source"])

            return bottle.template('postcode.html',
                result=result["_source"],
                postcode=result["_id"],
                point=None,
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                gmaps_api_key=GMAPS_API_KEY,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return result["_source"]

def process_postcode_result(postcode):
    for i in postcode:
        if postcode[i]:
            code = es.get(index='postcode', doc_type='code', id=postcode[i], ignore=[404])#, _source_include=["name"])
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
    # @TODO html version
    if areaname:
        result = es.search(index='postcode', doc_type='code', q=areaname, from_=from_, size=size)
        areas = [{"id": a["_id"], "name": a["_source"]["name"], "type": a["_source"]["type"]} for a in result["hits"]["hits"]]
        if filetype=="html":
            return bottle.template('areasearch.html',
            page=p, size=size, from_=from_,
            q=areaname,
            results=areas,
            result_count=result["hits"]["total"],
            area_types=AREA_TYPES,
            key_area_types=KEY_AREA_TYPES,
            gmaps_api_key=GMAPS_API_KEY,
            other_codes=OTHER_CODES
            )
        elif filetype=="json":
            return {"result": areas}

@bottle.route('/area/<areacode>')
@bottle.route('/area/<areacode>.<filetype>')
def area(areacode, filetype="json"):
    result = es.get(index='postcode', doc_type='code', id=areacode, ignore=[404])
    if result["found"]:
        # @TODO needs to be random order
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
        example = es.search(index='postcode', doc_type='postcode', body=query, size=5)
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
                gmaps_api_key=GMAPS_API_KEY,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return result["_source"]

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
    result = es.search(index='postcode', doc_type='code', body=query)
    area_counts = {i["key"]:i["doc_count"] for i in result["aggregations"]["group_by_type"]["buckets"]}


    if filetype=="html":
        return bottle.template('areatypes.html',
            area_counts=area_counts,
            area_types=AREA_TYPES,
            key_area_types=KEY_AREA_TYPES,
            gmaps_api_key=GMAPS_API_KEY,
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
    result = es.search(index='postcode', doc_type='code', body=query, from_=from_, size=size)
    if filetype=="html":
        return bottle.template('areatype.html',
            result=result["hits"]["hits"],
            count_areas = result["hits"]["total"],
            page=p, size=size, from_=from_,
            area_type=[a for a in AREA_TYPES if a[0]==areatype][0],
            area_types=AREA_TYPES,
            key_area_types=KEY_AREA_TYPES,
            gmaps_api_key=GMAPS_API_KEY,
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
    result = es.search(index='postcode', doc_type='postcode', body=query, size=1)
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
            gmaps_api_key=GMAPS_API_KEY,
            other_codes=OTHER_CODES
            )
    elif filetype=="json":
        return postcode["_source"]

@bottle.route('/static/<filename:path>')
def send_static(filename):
    """ if we need static files
    """
    return bottle.static_file(filename, root='./static')

bottle.run(reloader=True)
