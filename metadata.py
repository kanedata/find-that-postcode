AREA_TYPES = [
    ("oa11", "Output area", "2011 Census Output Area (OA)/ Small Area (SA)", "The 2011 Census OAs in GB and SAs in Northern Ireland were based on 2001 Census OAs, and they form the building bricks for defining higher level geographies. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no grid reference."),
    ("cty", "County", "County", "The current county to which the postcode has been assigned. Pseudo codes are included for English UAs, Wales, Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("laua", "Local Authority", "Local Authority District (LAD)/unitary authority (UA)/metropolitan district (MD)/London borough (LB)/ council area (CA)/district council area (DCA)", "The current district/UA to which the postcode has been assigned. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("ward", "Ward", "(Electoral) ward/division", "The current administrative/electoral area to which the postcode has been assigned. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("hlthau", "Strategic Health Authority", "Former Strategic Health Authority (SHA)/ Local Health Board (LHB)/ Health Board (HB)/ Health Authority (HA)/ Health & Social Care Board (HSCB)", "The health area code for the postcode. SHAs were abolished in England in 2013 but the codes remain as a 'frozen' geography. The field will otherwise be blank for postcodes with no OA code."),
    ("hro", "Pan SHA", "Pan SHA", "The Pan SHA responsible for the associated strategic health authority for each postcode in England. Pseudo codes are included for Wales, Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("ctry", "Country", "Country", "The code for the appropriate country (i.e. one of the four constituent countries of the UK or Crown dependencies - the Channel Islands or the Isle of Man) to which each postcode is assigned."),
    ("rgn", "Region", "Region (former GOR)", "The region code for each postcode. Pseudo codes are included for Wales, Scotland, Northern Ireland, Channel Island and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("pcon", "Westminster parliamentary constituency", "Westminster parliamentary constituency", "The Westminster parliamentary constituency code for each postcode. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("eer", "European Electoral Region", "European Electoral Region (EER)", "The European Electoral Region code for each postcode. A pseudo code is included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code"),
    ("teclec", "Local Learning and Skills Council", "Local Learning and Skills Council (LLSC)/ Dept. of Children, Education, Lifelong Learning and Skills (DCELLS)/Enterprise Region (ER)", "The LLSC (England), DCELLS (Wales) or ER (Scotland) code for each postcode. Pseudo codes are included for Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
    ("ttwa", "Travel to Work Area", "Travel to Work Area (TTWA)", "The TTWA code for the postcode. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code."),
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
    ("Key", ["ctry", "region", "cty", "laua", "ward", "oa11", "pcon", "rgn"]),
    ("Secondary", ["ttwa", "pfa", "lep", "msoa11", "lsoa11", "park"]),
    ("Health", ["ccg", "hlthau", "hro", "pct"]),
    ("Other", ["eer", "bua11", "buasd11", "wz11", "teclec", "nuts"]),
]

OTHER_CODES = {
    "osgrdind": [
        "",  # no code 0
        "within the building of the matched address closest to the postcode mean",
        "as for status value 1, except by visual inspection of Landline maps (Scotland only)",
        "approximate to within 50 metres",
        "postcode unit mean (mean of matched addresses with the same postcode, but not snapped to a building)",
        "imputed by ONS, by reference to surrounding postcode grid references",
        "postcode sector mean, (mainly PO Boxes)",
        "",  # code 7 missing
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


DEFAULT_UPLOAD_FIELDS = ["latlng", "laua", "laua_name", "rgn", "rgn_name"]
BASIC_UPLOAD_FIELDS = [
    ("latlng", "Latitude / Longitude", False),
    ("estnrth", "OS Easting / Northing", False),
    ("pcds", "Standardised postcode", False),
    ("imd", "Index of multiple deprivation rank", False),
    ("oac11", "2011 Output Area Classification (OAC)", True),
    ("ru11ind", "2011 Census rural-urban classification", True),
]


NAME_FILES = [
    {"file": "Documents/2011 Census Output Area Classification Names and Codes UK.csv", "type_field": "oac11", "code_field": "OAC11", "name_field": "Subgroup", "welsh_name_field": None},
    {"file": "Documents/BUASD_names and codes UK", "type_field": "buasd11", "code_field": "BUASD13CD", "name_field": "BUASD13NM", "welsh_name_field": None},
    {"file": "Documents/BUA_names and codes UK", "type_field": "bua11", "code_field": "BUA13CD", "name_field": "BUA13NM", "welsh_name_field": None},
    {"file": "Documents/CCG names and codes UK", "type_field": "ccg", "code_field": "CCG18CD", "name_field": "CCG18NM", "welsh_name_field": "CCG18NMW"},
    {"file": "Documents/Country names and codes UK", "type_field": "ctry", "code_field": "CTRY12CD", "name_field": "CTRY12NM", "welsh_name_field": "CTRY12NMW"},
    {"file": "Documents/County names and codes UK", "type_field": "cty", "code_field": "CTY10CD", "name_field": "CTY10NM", "welsh_name_field": None},
    {"file": "Documents/EER names and codes UK", "type_field": "eer", "code_field": "EER10CD", "name_field": "EER10NM", "welsh_name_field": None},
    {"file": "Documents/HLTHAU names and codes UK", "type_field": "hlthau", "code_field": "HLTHAUCD", "name_field": "HLTHAUNM", "welsh_name_field": "HLTHAUNMW"},
    {"file": "Documents/LAU2 names and codes UK", "type_field": "nuts", "code_field": "LAU216CD", "name_field": "LAU216NM", "welsh_name_field": None},
    {"file": "Documents/LA_UA names and codes UK", "type_field": "laua", "code_field": "LAD16CD", "name_field": "LAD16NM", "welsh_name_field": None},
    {"file": "Documents/LEP names and codes EN", "type_field": "lep", "code_field": "LEP13CD1", "name_field": "LEP13NM1", "welsh_name_field": None},
    {"file": "Documents/LSOA (2011) names and codes UK", "type_field": "lsoa11", "code_field": "LSOA11CD", "name_field": "LSOA11NM", "welsh_name_field": None},
    {"file": "Documents/MSOA (2011) names and codes UK", "type_field": "msoa11", "code_field": "MSOA11CD", "name_field": "MSOA11NM", "welsh_name_field": None},
    {"file": "Documents/National Park names and codes GB", "type_field": "park", "code_field": "NPARK16CD", "name_field": "NPARK16NM", "welsh_name_field": None},
    {"file": "Documents/Pan SHA names and codes EN", "type_field": "hro", "code_field": "PSHA10CD", "name_field": "PSHA10NM", "welsh_name_field": None},
    {"file": "Documents/PCT names and codes UK", "type_field": "pct", "code_field": "PCTCD", "name_field": "PCTNM", "welsh_name_field": "PCTNMW"},
    {"file": "Documents/PFA names and codes GB", "type_field": "pfa", "code_field": "PFA15CD", "name_field": "PFA15NM", "welsh_name_field": None},
    {"file": "Documents/Region names and codes EN", "type_field": "rgn", "code_field": "GOR10CD", "name_field": "GOR10NM", "welsh_name_field": "GOR10NMW"},
    {"file": "Documents/Rural Urban (2011) Indicator names and codes GB", "type_field": "ru11ind", "code_field": "RU11IND", "name_field": "RU11NM", "welsh_name_field": None},
    {"file": "Documents/TECLEC names and codes UK", "type_field": "teclec", "code_field": "TECLECCD", "name_field": "TECLECNM", "welsh_name_field": None},
    {"file": "Documents/TTWA names and codes UK", "type_field": "ttwa", "code_field": "TTWA11CD", "name_field": "TTWA11NM", "welsh_name_field": None},
    {"file": "Documents/Westminster Parliamentary Constituency names and codes UK", "type_field": "pcon", "code_field": "PCON14CD", "name_field": "PCON14NM", "welsh_name_field": None},
    {"file": "Documents/Ward names and codes UK", "type_field": "ward", "code_field": "WD16CD", "name_field": "WD16NM", "welsh_name_field": None},
    # {"file": "Documents/LAU216_LAU116_NUTS315_NUTS215_NUTS115_UK_LU.csv", "type_field": "", "name_field": "", "welsh_name_field": None},
]
