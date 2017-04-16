from metadata import AREA_TYPES

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

def get_area_type(areatype):
    possible_types = [a for a in AREA_TYPES if a[0]==areatype]
    if len(possible_types)==1:
        return possible_types[0]
    return []


def get_area_link(areaid, filetype=None):
    return "/areas/{}{}".format(areaid, set_url_filetype(filetype))


def set_url_filetype(filetype=None):
    if filetype:
        return "." + filetype
    return ""

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
