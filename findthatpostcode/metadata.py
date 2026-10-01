import json
import os

from findthatpostcode.utils import Field

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "areatypes.json")
) as a:
    AREA_TYPES = json.load(a)
    for k in AREA_TYPES:
        AREA_TYPES[k]["countries"] = list(
            {e[0] for e in AREA_TYPES[k]["entities"]}
        )
    AREA_THEMES = list({a["theme"] for a in AREA_TYPES.values()})
    ENTITIES = {e: k for k, v in AREA_TYPES.items() for e in v["entities"]}

KEY_AREA_TYPES = [
    ("Key", ["ctry", "rgn", "cty", "laua", "ward", "msoa21", "pcon"]),
    ("Secondary", ["ttwa", "pfa", "lsoa21", "oa21", "npark"]),
    ("Health", ["ccg", "nhser", "hb", "lhb", "icb"]),
    ("Other / inactive", ["lep", "eer", "bua11", "buasd11", "wz11", "teclec"]),
]

OTHER_CODES = {
    "osgrdind": [
        "",  # no code 0
        "within the building of the matched address closest to the postcode mean",
        (
            "as for status value 1, except by visual "
            "inspection of Landline maps (Scotland only)"
        ),
        "approximate to within 50 metres",
        (
            "postcode unit mean (mean of matched addresses "
            "with the same postcode, but not snapped to a building)"
        ),
        "imputed by ONS, by reference to surrounding postcode grid references",
        "postcode sector mean, (mainly PO Boxes)",
        "",  # code 7 missing
        (
            "postcode terminated prior to Gridlink(R) initiative, "
            "last known ONS postcode grid reference"
        ),
        "no grid reference available",
    ],
    "usertype": ["Small user", "Large user"],
    "imd": {
        "E92000001-imd2025": 33755,
        "W92000004-imd2025": 1909,
        "S92000003-imd2025": 6976,
        "N92000002-imd2025": None,
        "L93000001-imd2025": None,
        "M83000003-imd2025": None,
        "E92000001-imd2019": 32844,
        "W92000004-imd2019": 1909,
        "S92000003-imd2019": 6976,
        "N92000002-imd2019": None,
        "L93000001-imd2019": None,
        "M83000003-imd2019": None,
        "E92000001-imd2015": 32844,
        "W92000004-imd2015": 1909,
        "S92000003-imd2015": 6976,
        "N92000002-imd2015": None,
        "L93000001-imd2015": None,
        "M83000003-imd2015": None,
    },
}


DEFAULT_UPLOAD_FIELDS = ["latlng", "laua", "laua_name", "rgn", "rgn_name"]
BASIC_UPLOAD_FIELDS = [
    Field(id="latlng", name="Latitude / Longitude", has_name=False),
    Field(id="estnrth", name="OS Easting / Northing", has_name=False),
    Field(id="pcds", name="Standardised postcode", has_name=False),
    Field(id="oac21", name="2021 Output Area Classification (OAC)", has_name=True),
    Field(id="ru11ind", name="2011 Census rural-urban classification", has_name=True),
    Field(id="ruc21", name="2021 Census rural-urban classification", has_name=True),
]
STATS_FIELDS = [
    Field(
        id="imd2025_rank",
        name="Index of multiple deprivation (2025) rank",
        location="stats.imd2025.imd_rank",
        area="lsoa21",
    ),
    Field(
        id="imd2025_decile",
        name="Index of multiple deprivation (2025) decile",
        location="stats.imd2025.imd_decile",
        area="lsoa21",
    ),
    Field(
        id="imd2019_rank",
        name="Index of multiple deprivation (2019) rank",
        location="stats.imd2019.imd_rank",
        area="lsoa11",
    ),
    Field(
        id="imd2019_decile",
        name="Index of multiple deprivation (2019) decile",
        location="stats.imd2019.imd_decile",
        area="lsoa11",
    ),
    Field(
        id="imd2015_rank",
        name="Index of multiple deprivation (2015) rank",
        location="stats.imd2015.imd_rank",
        area="lsoa11",
    ),
    Field(
        id="imd2015_decile",
        name="Index of multiple deprivation (2015) decile",
        location="stats.imd2015.imd_decile",
        area="lsoa11",
    ),
    # Field(
    #   id="popn2015",
    #   name="Total population (2015)",
    #   location="stats.population2015.population_total",
    #   area="lsoa11",
    # ),
]

# "Supergroup", "Group", "Subgroup"],
OAC11_CODE = {
    "1A1": ["Rural residents", "Farming communities", "Rural workers and families"],
    "1A2": [
        "Rural residents",
        "Farming communities",
        "Established farming communities",
    ],
    "1A3": ["Rural residents", "Farming communities", "Agricultural communities"],
    "1A4": ["Rural residents", "Farming communities", "Older farming communities"],
    "1B1": ["Rural residents", "Rural tenants", "Rural life"],
    "1B2": ["Rural residents", "Rural tenants", "Rural white-collar workers"],
    "1B3": ["Rural residents", "Rural tenants", "Ageing rural flat tenants"],
    "1C1": [
        "Rural residents",
        "Ageing rural dwellers",
        "Rural employment and retirees",
    ],
    "1C2": ["Rural residents", "Ageing rural dwellers", "Renting rural retirement"],
    "1C3": ["Rural residents", "Ageing rural dwellers", "Detached rural retirement"],
    "2A1": ["Cosmopolitans", "Students around campus", "Student communal living"],
    "2A2": ["Cosmopolitans", "Students around campus", "Student digs"],
    "2A3": ["Cosmopolitans", "Students around campus", "Students and professionals"],
    "2B1": ["Cosmopolitans", "Inner city students", "Students and commuters"],
    "2B2": [
        "Cosmopolitans",
        "Inner city students",
        "Multicultural student neighbourhood",
    ],
    "2C1": ["Cosmopolitans", "Comfortable cosmopolitan", "Migrant families"],
    "2C2": ["Cosmopolitans", "Comfortable cosmopolitan", "Migrant commuters"],
    "2C3": [
        "Cosmopolitans",
        "Comfortable cosmopolitan",
        "Professional service cosmopolitans",
    ],
    "2D1": ["Cosmopolitans", "Aspiring and affluent", "Urban cultural mix"],
    "2D2": [
        "Cosmopolitans",
        "Aspiring and affluent",
        "Highly-qualified quaternary workers",
    ],
    "2D3": ["Cosmopolitans", "Aspiring and affluent", "EU white-collar workers"],
    "3A1": ["Ethnicity central", "Ethnic family life", "Established renting families"],
    "3A2": ["Ethnicity central", "Ethnic family life", "Young families and students"],
    "3B1": ["Ethnicity central", "Endeavouring ethnic mix", "Striving service workers"],
    "3B2": [
        "Ethnicity central",
        "Endeavouring ethnic mix",
        "Bangladeshi mixed employment",
    ],
    "3B3": [
        "Ethnicity central",
        "Endeavouring ethnic mix",
        "Multi-ethnic professional service workers",
    ],
    "3C1": ["Ethnicity central", "Ethnic dynamics", "Constrained neighbourhoods"],
    "3C2": ["Ethnicity central", "Ethnic dynamics", "Constrained commuters"],
    "3D1": ["Ethnicity central", "Aspirational techies", "New EU tech workers"],
    "3D2": ["Ethnicity central", "Aspirational techies", "Established tech workers"],
    "3D3": ["Ethnicity central", "Aspirational techies", "Old EU tech workers"],
    "4A1": [
        "Multicultural metropolitans",
        "Rented family living",
        "Social renting young families",
    ],
    "4A2": [
        "Multicultural metropolitans",
        "Rented family living",
        "Private renting new arrivals",
    ],
    "4A3": [
        "Multicultural metropolitans",
        "Rented family living",
        "Commuters with young families",
    ],
    "4B1": [
        "Multicultural metropolitans",
        "Challenged Asian terraces",
        "Asian terraces and flats",
    ],
    "4B2": [
        "Multicultural metropolitans",
        "Challenged Asian terraces",
        "Pakistani communities",
    ],
    "4C1": ["Multicultural metropolitans", "Asian traits", "Achieving minorities"],
    "4C2": [
        "Multicultural metropolitans",
        "Asian traits",
        "Multicultural new arrivals",
    ],
    "4C3": ["Multicultural metropolitans", "Asian traits", "Inner city ethnic mix"],
    "5A1": ["Urbanites", "Urban professionals and families", "White professionals"],
    "5A2": [
        "Urbanites",
        "Urban professionals and families",
        "Multi-ethnic professionals with families",
    ],
    "5A3": [
        "Urbanites",
        "Urban professionals and families",
        "Families in terraces and flats",
    ],
    "5B1": ["Urbanites", "Ageing urban living", "Delayed retirement"],
    "5B2": ["Urbanites", "Ageing urban living", "Communal retirement"],
    "5B3": ["Urbanites", "Ageing urban living", "Self-sufficient retirement"],
    "6A1": ["Suburbanites", "Suburban achievers", "Indian tech achievers"],
    "6A2": ["Suburbanites", "Suburban achievers", "Comfortable suburbia"],
    "6A3": ["Suburbanites", "Suburban achievers", "Detached retirement living"],
    "6A4": ["Suburbanites", "Suburban achievers", "Ageing in suburbia"],
    "6B1": ["Suburbanites", "Semi-detached suburbia", "Multi-ethnic suburbia"],
    "6B2": ["Suburbanites", "Semi-detached suburbia", "White suburban communities"],
    "6B3": ["Suburbanites", "Semi-detached suburbia", "Semi-detached ageing"],
    "6B4": ["Suburbanites", "Semi-detached suburbia", "Older workers and retirement"],
    "7A1": [
        "Constrained city dwellers",
        "Challenged diversity",
        "Transitional Eastern European neighbourhood",
    ],
    "7A2": ["Constrained city dwellers", "Challenged diversity", "Hampered aspiration"],
    "7A3": [
        "Constrained city dwellers",
        "Challenged diversity",
        "Multi-ethnic hardship",
    ],
    "7B1": [
        "Constrained city dwellers",
        "Constrained flat dwellers",
        "Eastern European communities",
    ],
    "7B2": [
        "Constrained city dwellers",
        "Constrained flat dwellers",
        "Deprived neighbourhoods",
    ],
    "7B3": [
        "Constrained city dwellers",
        "Constrained flat dwellers",
        "Endeavouring flat dwellers",
    ],
    "7C1": [
        "Constrained city dwellers",
        "White communities",
        "Challenged transitionaries",
    ],
    "7C2": [
        "Constrained city dwellers",
        "White communities",
        "Constrained young families",
    ],
    "7C3": ["Constrained city dwellers", "White communities", "Outer city hardship"],
    "7D1": [
        "Constrained city dwellers",
        "Ageing city dwellers",
        "Ageing communities and families",
    ],
    "7D2": [
        "Constrained city dwellers",
        "Ageing city dwellers",
        "Retired independent city dwellers",
    ],
    "7D3": [
        "Constrained city dwellers",
        "Ageing city dwellers",
        "Retired communal city dwellers",
    ],
    "7D4": [
        "Constrained city dwellers",
        "Ageing city dwellers",
        "Retired city hardship",
    ],
    "8A1": [
        "Hard-pressed living",
        "Industrious communities",
        "Industrious transitions",
    ],
    "8A2": ["Hard-pressed living", "Industrious communities", "Industrious hardship"],
    "8B1": [
        "Hard-pressed living",
        "Challenged terraced workers",
        "Deprived blue-collar terraces",
    ],
    "8B2": [
        "Hard-pressed living",
        "Challenged terraced workers",
        "Hard pressed rented terraces",
    ],
    "8C1": [
        "Hard-pressed living",
        "Hard pressed ageing workers",
        "Ageing industrious workers",
    ],
    "8C2": [
        "Hard-pressed living",
        "Hard pressed ageing workers",
        "Ageing rural industry workers",
    ],
    "8C3": [
        "Hard-pressed living",
        "Hard pressed ageing workers",
        "Renting hard-pressed workers",
    ],
    "8D1": [
        "Hard-pressed living",
        "Migration and churn",
        "Young hard-pressed families",
    ],
    "8D2": ["Hard-pressed living", "Migration and churn", "Hard-pressed ethnic mix"],
    "8D3": [
        "Hard-pressed living",
        "Migration and churn",
        "Hard-Pressed European Settlers",
    ],
    "9Z9": ["(pseudo) CI, IoM", "(pseudo) CI, IoM", "(pseudo) CI, IoM"],
}

OAC21_CODE = {
    "1A1": [
        "Retired Professionals",
        "Spacious Rural Living",
        "Pre-Retirement Spacious Living",
    ],
    "1A2": [
        "Retired Professionals",
        "Spacious Rural Living",
        "Retirement Spacious Living",
    ],
    "1B1": [
        "Retired Professionals",
        "Small Town Suburbia",
        "Younger Established Suburban Communities",
    ],
    "1B2": [
        "Retired Professionals",
        "Small Town Suburbia",
        "Older Established Suburban Communities",
    ],
    "1C1": [
        "Retired Professionals",
        "Established Mature Families",
        "Affluent Mature Families",
    ],
    "1C2": [
        "Retired Professionals",
        "Established Mature Families",
        "Burgeoning Mature Families",
    ],
    "2A1": [
        "Suburbanites and Peri-Urbanites",
        "Inner Suburbs and Small Town Living",
        "Younger Suburban Family Renters",
    ],
    "2A2": [
        "Suburbanites and Peri-Urbanites",
        "Inner Suburbs and Small Town Living",
        "Settled Owner-Occupied Suburbs",
    ],
    "2A3": [
        "Suburbanites and Peri-Urbanites",
        "Inner Suburbs and Small Town Living",
        "Terraced Communities",
    ],
    "2B1": [
        "Suburbanites and Peri-Urbanites",
        "Rural Amenity",
        "Ageing Rural Communities",
    ],
    "2B2": ["Suburbanites and Peri-Urbanites", "Rural Amenity", "Rural Mix"],
    "2C1": [
        "Suburbanites and Peri-Urbanites",
        "Ageing Communities",
        "Communal Retirement Living",
    ],
    "2C2": [
        "Suburbanites and Peri-Urbanites",
        "Ageing Communities",
        "Ageing Independent Living",
    ],
    "3A1": [
        "Multicultural and Educated Urbanites",
        "Student Living and Professional Footholds",
        "University Centric",
    ],
    "3A2": [
        "Multicultural and Educated Urbanites",
        "Student Living and Professional Footholds",
        "Professional Progression",
    ],
    "3A3": [
        "Multicultural and Educated Urbanites",
        "Student Living and Professional Footholds",
        "Urbanite Mix",
    ],
    "3A4": [
        "Multicultural and Educated Urbanites",
        "Student Living and Professional Footholds",
        "Affluent Graduate Living",
    ],
    "3B1": [
        "Multicultural and Educated Urbanites",
        "Ethnically Diverse Young Families",
        "Private Rental Ethnic Minority Families",
    ],
    "3B2": [
        "Multicultural and Educated Urbanites",
        "Ethnically Diverse Young Families",
        "Young Ethnic Minority Families",
    ],
    "3C1": [
        "Multicultural and Educated Urbanites",
        "Diverse Educated Urban Singles",
        "Centrally Located Professionals",
    ],
    "3C2": [
        "Multicultural and Educated Urbanites",
        "Diverse Educated Urban Singles",
        "Career Progression",
    ],
    "4A1": [
        "Low-Skilled Migrant and Student Communities",
        "Ethnically Diverse Families in Less Connected Locations",
        "Semi-Detached, Service Workers and Students",
    ],
    "4A2": [
        "Low-Skilled Migrant and Student Communities",
        "Ethnically Diverse Families in Less Connected Locations",
        "City Service Workers",
    ],
    "4A3": [
        "Low-Skilled Migrant and Student Communities",
        "Ethnically Diverse Families in Less Connected Locations",
        "Multi-Child Young Families",
    ],
    "4B1": [
        "Low-Skilled Migrant and Student Communities",
        "Established Multi- Ethnic Communities",
        "Migrant Families",
    ],
    "4B2": [
        "Low-Skilled Migrant and Student Communities",
        "Established Multi- Ethnic Communities",
        "European Skilled Workforce",
    ],
    "4B3": [
        "Low-Skilled Migrant and Student Communities",
        "Established Multi- Ethnic Communities",
        "Inner Suburb Ethnic Group Mix",
    ],
    "4B4": [
        "Low-Skilled Migrant and Student Communities",
        "Established Multi- Ethnic Communities",
        "Ethnic Minority Routine Service Workers",
    ],
    "4C1": [
        "Low-Skilled Migrant and Student Communities",
        "Challenged Multicultural Communities and Students",
        "African and Asian Influences",
    ],
    "4C2": [
        "Low-Skilled Migrant and Student Communities",
        "Challenged Multicultural Communities and Students",
        "European and Asian Heritage",
    ],
    "5A1": [
        "Ethnically Diverse Suburb-an Professionals",
        "Outer Suburbs",
        "Outer Suburb Asian Mix",
    ],
    "5A2": [
        "Ethnically Diverse Suburb-an Professionals",
        "Outer Suburbs",
        "Suburban Empty Nesters",
    ],
    "5A3": [
        "Ethnically Diverse Suburb-an Professionals",
        "Outer Suburbs",
        "Young Suburban Families",
    ],
    "5B1": [
        "Ethnically Diverse Suburb-an Professionals",
        "Suburban Professionals",
        "Families in Multi-Ethnic Terraces",
    ],
    "5B2": [
        "Ethnically Diverse Suburb-an Professionals",
        "Suburban Professionals",
        "Established Multi-Ethnic Suburbs",
    ],
    "6A1": ["Baseline UK", "Challenged Communities", "Suburban Housing Starters"],
    "6A2": ["Baseline UK", "Challenged Communities", "Semi Detached Strivers"],
    "6A3": [
        "Baseline UK",
        "Challenged Communities",
        "Younger Ethnic Minority Families in Flats",
    ],
    "6B1": [
        "Baseline UK",
        "Legacy Industrial and Coastal Communities",
        "Retired Seniors",
    ],
    "6B2": [
        "Baseline UK",
        "Legacy Industrial and Coastal Communities",
        "Traditional Terraces",
    ],
    "6B3": ["Baseline UK", "Legacy Industrial and Coastal Communities", "EU Singles"],
    "6C1": ["Baseline UK", "Multicultural Inner Suburbs", "Transient Communities"],
    "6C2": [
        "Baseline UK",
        "Multicultural Inner Suburbs",
        "Semi-Detached Family Renters",
    ],
    "7A1": [
        "Semi- and Un-Skilled Workforce",
        "Established but Challenged",
        "Ageing Established Urban Communities",
    ],
    "7A2": [
        "Semi- and Un-Skilled Workforce",
        "Established but Challenged",
        "Industry Associations",
    ],
    "7B1": [
        "Semi- and Un-Skilled Workforce",
        "Young Families in Industrial Towns",
        "Terraces in Transitional Towns",
    ],
    "7B2": [
        "Semi- and Un-Skilled Workforce",
        "Young Families in Industrial Towns",
        "Families and Later Life",
    ],
    "8A1": [
        "Legacy Communities",
        "Routine Occupations or Retirement",
        "Retirement Residences",
    ],
    "8A2": [
        "Legacy Communities",
        "Routine Occupations or Retirement",
        "Flats and Routine Occupations",
    ],
    "8B1": [
        "Legacy Communities",
        "Legacy and Demographically Mixed Communities",
        "Challenged Families",
    ],
    "8B2": [
        "Legacy Communities",
        "Legacy and Demographically Mixed Communities",
        "Retirement Pockets",
    ],
    "8B3": [
        "Legacy Communities",
        "Legacy and Demographically Mixed Communities",
        "Young Family Flat Renters",
    ],
}

RU11IND_CODES = {
    "A1": "Urban major conurbation",
    "B1": "Urban minor conurbation",
    "C1": "Urban city and town",
    "C2": "Urban city and town in a sparse setting",
    "D1": "Rural town and fringe",
    "D2": "Rural town and fringe in a sparse setting",
    "E1": "Rural village",
    "E2": "Rural village in a sparse setting",
    "F1": "Rural hamlet and isolated dwellings",
    "F2": "Rural hamlet and isolated dwellings in a sparse setting",
    "1": "Large Urban Area",
    "2": "Other Urban Area",
    "3": "Accessible Small Town",
    "4": "Remote Small Town",
    "5": "Very Remote Small Town",
    "6": "Accessible Rural",
    "7": "Remote Rural",
    "8": "Very Remote Rural",
}

RUC21_CODES = {
    "RLF1": "Larger rural: Further from a major town or city",  # Rural
    "RLN1": "Larger rural: Nearer to a major town or city",  # Rural
    "RSF1": "Smaller rural: Further from a major town or city",  # Rural
    "RSN1": "Smaller rural: Nearer to a major town or city",  # Rural
    "UF1": "Urban: Further from a major town or city",  # Urban
    "UN1": "Urban: Nearer to a major town or city",  # Urban
}
