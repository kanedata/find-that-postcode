# Auto-generated from JSON file
import enum


class AreaTypeEnum(str, enum.Enum):
    AGRICREG = "agricreg"
    AGRICSMALL = "agricsmall"
    BRMA = "brma"
    BUA11 = "bua11"
    BUASD11 = "buasd11"
    CAL = "cal"
    CANNET = "cannet"
    CANREG = "canreg"
    CAUTH = "cauth"
    CCG = "ccg"
    CDC = "cdc"
    CED = "ced"
    CFA = "cfa"
    CHCP = "chcp"
    CHP = "chp"
    CJA = "cja"
    CLC = "clc"
    CMCTY = "cmcty"
    CMLAD = "cmlad"
    CMWD = "cmwd"
    COM = "com"
    CREG = "creg"
    CSP = "csp"
    CT = "ct"
    CTRY = "ctry"
    CTY = "cty"
    CTY1961 = "cty1961"
    CVP = "cvp"
    DC = "dc"
    DCELLS = "dcells"
    DEA = "dea"
    EER = "eer"
    ER = "er"
    EZ = "ez"
    FRA = "fra"
    GLA = "gla"
    HB = "hb"
    HIA = "hia"
    HIE = "hie"
    ICB = "icb"
    ICS = "ics"
    IOL = "iol"
    ISDT = "isdt"
    ISLG = "islg"
    LAC = "lac"
    LAD1961 = "lad1961"
    LAU1 = "lau1"
    LAU2 = "lau2"
    LAUA = "laua"
    LEP = "lep"
    LEPNOP = "lepnop"
    LEPOP = "lepop"
    LHB = "lhb"
    LLSC = "llsc"
    LOC = "loc"
    LPA = "lpa"
    LRF = "lrf"
    LSOA11 = "lsoa11"
    LSOA21 = "lsoa21"
    MCTY = "mcty"
    MSOA11 = "msoa11"
    MSOA21 = "msoa21"
    NAER = "naer"
    NAWC = "nawc"
    NAWER = "nawer"
    NCP = "ncp"
    NCV = "ncv"
    NDC = "ndc"
    NHSER = "nhser"
    NHSRLO = "nhsrlo"
    NIFRS = "nifrs"
    NIFRSA = "nifrsa"
    NIFRSD = "nifrsd"
    NONCFA = "noncfa"
    NONNPARK = "nonnpark"
    NONSRA = "nonsra"
    NPARK = "npark"
    OA11 = "oa11"
    OA21 = "oa21"
    PAR = "par"
    PAR1961 = "par1961"
    PCON = "pcon"
    PCT = "pct"
    PFA = "pfa"
    PFD = "pfd"
    PHD = "phd"
    PHEC = "phec"
    PHEREG = "phereg"
    PSCREG = "pscreg"
    PSHA = "psha"
    PUA = "pua"
    REGD = "regd"
    REGSD = "regsd"
    RGN = "rgn"
    ROAC = "roac"
    ROAL = "roal"
    ROAS = "roas"
    RTP = "rtp"
    SCN = "scn"
    SDPA = "sdpa"
    SETT = "sett"
    SETT2015 = "sett2015"
    SFRLSO = "sfrlso"
    SFRS = "sfrs"
    SFRSDA = "sfrsda"
    SHA = "sha"
    SLRP = "slrp"
    SMR = "smr"
    SPA = "spa"
    SPC = "spc"
    SPD = "spd"
    SPR = "spr"
    SPSA = "spsa"
    SRA = "sra"
    SRASUB = "srasub"
    SRRP = "srrp"
    TCA = "tca"
    TCITY = "tcity"
    TTWA = "ttwa"
    URC = "urc"
    USOA = "usoa"
    WA = "wa"
    WARD = "ward"
    WARD1961 = "ward1961"
    WZ11 = "wz11"


AREA_TYPES = {
    AreaTypeEnum.AGRICREG: {
        "entities": ["W29"],
        "status": "Current",
        "theme": "Other",
        "name": "Agricultural Regions",
        "full_name": "Agricultural Regions",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.AGRICSMALL: {
        "entities": ["W30"],
        "status": "Current",
        "theme": "Other",
        "name": "Agricultural Small Areas",
        "full_name": "Agricultural Small Areas",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.BRMA: {
        "entities": ["S33"],
        "status": "Current",
        "theme": "Housing and Regeneration",
        "name": "Broad Rental Market Areas",
        "full_name": "Broad Rental Market Areas",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.BUA11: {
        "entities": ["E34", "K05", "W37"],
        "status": "Current",
        "theme": "Census",
        "name": "Built-up Area",
        "full_name": "Built-up Area (BUA)",
        "description": "The code for the BUAs in England and Wales. Pseudo codes are included for those OAs not classed as 'built-up' and cross-border codes are included for areas straddling the English/Welsh border. Pseudo codes are also included for Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["K", "W", "E"],
    },
    AreaTypeEnum.BUASD11: {
        "entities": ["E35", "K06", "W38"],
        "status": "Current",
        "theme": "Census",
        "name": "Built-up Area Sub-division (BUASD)",
        "full_name": "Built-up Area Sub-division",
        "description": "The code for the BUASDs in England and Wales. Pseudo codes are included for those OAs not classed as 'built-up' and cross-border codes are included for areas straddling the English/Welsh border. Pseudo codes are also included for Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code",
        "countries": ["K", "W", "E"],
    },
    AreaTypeEnum.CAL: {
        "entities": ["E56"],
        "status": "Current",
        "theme": "Health",
        "name": "Cancer Alliances",
        "full_name": "Cancer Alliances",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.CANNET: {
        "entities": ["E21", "W13"],
        "status": "Current",
        "theme": "Health",
        "name": "Cancer Networks",
        "full_name": "Cancer Networks",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.CANREG: {
        "entities": ["E20", "W12"],
        "status": "Current",
        "theme": "Health",
        "name": "Cancer Registries",
        "full_name": "Cancer Registries",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.CAUTH: {
        "entities": ["E47"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Combined Authorities",
        "full_name": "Combined Authorities",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.CCG: {
        "entities": ["E38"],
        "status": "Current",
        "theme": "Health",
        "name": "Clinical Commissioning Group",
        "full_name": "Clinical Commissioning Group (CCG)/Local Health Board (LHB)/Community Health Partnership (CHP)/ Local Commissioning Group (LCG)/Primary Healthcare Directorate (PHD)",
        "description": "The code for the CCG areas in England, LHBs in Wales, CHPs in Scotland, LCG in Northern Ireland and PHD in the Isle of Man. A pseudo code is included for Channel Islands. The field will be blank for postcodes in England or Wales with no OA code.",
        "countries": ["E"],
    },
    AreaTypeEnum.CDC: {
        "entities": ["S28"],
        "status": "Current",
        "theme": "Census",
        "name": "Census Detailed Characteristics",
        "full_name": "Census Detailed Characteristics",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.CED: {
        "entities": ["E58"],
        "status": "Current",
        "theme": "Electoral",
        "name": "County Electoral Divisions",
        "full_name": "County Electoral Divisions",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.CFA: {
        "entities": ["W33"],
        "status": "Current",
        "theme": "Other",
        "name": "Communities First Areas",
        "full_name": "Communities First Areas",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.CHCP: {
        "entities": ["S26"],
        "status": "Archived",
        "theme": "Health",
        "name": "Community Health Partnerships sub-areas",
        "full_name": "Community Health Partnerships sub-areas",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.CHP: {
        "entities": ["S03"],
        "status": "Archived",
        "theme": "Health",
        "name": "Community Health Partnerships",
        "full_name": "Community Health Partnerships",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.CJA: {
        "entities": ["S25"],
        "status": "Current",
        "theme": "Other",
        "name": "Community Justice Authorities",
        "full_name": "Community Justice Authorities",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.CLC: {
        "entities": ["S29"],
        "status": "Current",
        "theme": "Census",
        "name": "Census Local Characteristics",
        "full_name": "Census Local Characteristics",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.CMCTY: {
        "entities": ["E42"],
        "status": "Current",
        "theme": "Census",
        "name": "Census Merged Counties",
        "full_name": "Census Merged Counties",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.CMLAD: {
        "entities": ["E41", "W40"],
        "status": "Current",
        "theme": "Census",
        "name": "Census Merged Local Authority Districts",
        "full_name": "Census Merged Local Authority Districts",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.CMWD: {
        "entities": ["E36", "W39"],
        "status": "Current",
        "theme": "Census",
        "name": "Census Merged Wards",
        "full_name": "Census Merged Wards",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.COM: {
        "entities": ["W04"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Communities",
        "full_name": "Communities",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.CREG: {
        "entities": ["W42"],
        "status": "Current",
        "theme": "Other",
        "name": "City Regions",
        "full_name": "City Regions",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.CSP: {
        "entities": ["E22", "W14"],
        "status": "Current",
        "theme": "Other",
        "name": "Community Safety Partnerships",
        "full_name": "Community Safety Partnerships",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.CT: {
        "entities": ["E17"],
        "status": "Archived",
        "theme": "Health",
        "name": "Care Trusts",
        "full_name": "Care Trusts",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.CTRY: {
        "entities": ["E92", "K02", "K03", "K04", "L93", "M83", "N92", "S92", "W92"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Country",
        "full_name": "Country",
        "description": "The code for the appropriate country (i.e. one of the four constituent countries of the UK or Crown dependencies - the Channel Islands or the Isle of Man) to which each postcode is assigned.",
        "countries": ["K", "E", "L", "N", "S", "M", "W"],
    },
    AreaTypeEnum.CTY: {
        "entities": ["E10"],
        "status": "Current",
        "theme": "Administrative",
        "name": "County",
        "full_name": "County",
        "description": "The current county to which the postcode has been assigned. Pseudo codes are included for English UAs, Wales, Scotland, Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["E"],
    },
    AreaTypeEnum.CTY1961: {
        "entities": ["J05"],
        "status": "Current",
        "theme": "Census",
        "name": "1961 Census Counties",
        "full_name": "1961 Census Counties",
        "description": None,
        "countries": ["J"],
    },
    AreaTypeEnum.CVP: {
        "entities": ["S35"],
        "status": "Archived",
        "theme": "Administrative",
        "name": "Civil Parish",
        "full_name": "Civil Parish",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.DC: {
        "entities": ["E51"],
        "status": "Current",
        "theme": "Other",
        "name": "Development Corporations",
        "full_name": "Development Corporations",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.DCELLS: {
        "entities": ["W16"],
        "status": "Current",
        "theme": "Other",
        "name": "Department for Children, Education, Lifelong Learning and Skills, WG",
        "full_name": "Department for Children, Education, Lifelong Learning and Skills, WG",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.DEA: {
        "entities": ["N10"],
        "status": "Current",
        "theme": "Electoral",
        "name": "District Electoral Areas",
        "full_name": "District Electoral Areas",
        "description": None,
        "countries": ["N"],
    },
    AreaTypeEnum.EER: {
        "entities": ["E15", "N07", "S15", "W08"],
        "status": "Current",
        "theme": "Electoral",
        "name": "European Electoral Region",
        "full_name": "European Electoral Region (EER)",
        "description": "The European Electoral Region code for each postcode. A pseudo code is included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code",
        "countries": ["N", "W", "S", "E"],
    },
    AreaTypeEnum.ER: {
        "entities": ["S09"],
        "status": "Current",
        "theme": "Economic",
        "name": "Enterprise Regions",
        "full_name": "Enterprise Regions",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.EZ: {
        "entities": ["E49"],
        "status": "Current",
        "theme": "Other",
        "name": "Enterprise Zones",
        "full_name": "Enterprise Zones",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.FRA: {
        "entities": ["E31", "W25"],
        "status": "Current",
        "theme": "Other",
        "name": "Fire and Rescue Authorities",
        "full_name": "Fire and Rescue Authorities",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.GLA: {
        "entities": ["E61"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Greater London Authority",
        "full_name": "Greater London Authority",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.HB: {
        "entities": ["S08"],
        "status": "Current",
        "theme": "Health",
        "name": "Health Board areas",
        "full_name": "Health Board areas",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.HIA: {
        "entities": ["S37"],
        "status": "Current",
        "theme": "Health",
        "name": "Integration Authorities",
        "full_name": "Integration Authorities",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.HIE: {
        "entities": ["S24"],
        "status": "Current",
        "theme": "Economic",
        "name": "Highlands and Islands Enterprise",
        "full_name": "Highlands and Islands Enterprise",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.ICB: {
        "entities": ["E54"],
        "status": "Current",
        "theme": "Health",
        "name": "Integrated Care Board",
        "full_name": "Integrated Care Board (ICB)",
        "description": "The code for the ICB areas in England. A pseudo code is included for Channel Islands. The field will be blank for postcodes in England with no OA code.",
        "countries": ["E"],
    },
    AreaTypeEnum.ICS: {
        "entities": ["E59"],
        "status": "Current",
        "theme": "Health",
        "name": "Integrated Care Systems",
        "full_name": "Integrated Care Systems",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.IOL: {
        "entities": ["E13"],
        "status": "Current",
        "theme": "Statistical Building Block",
        "name": "Inner and Outer London",
        "full_name": "Inner and Outer London",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.ISDT: {
        "entities": ["S27"],
        "status": "Current",
        "theme": "Health",
        "name": "ISD Health Board of Treatment",
        "full_name": "ISD Health Board of Treatment",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.ISLG: {
        "entities": ["S36"],
        "status": "Current",
        "theme": "Other",
        "name": "Island Groups",
        "full_name": "Island Groups",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.LAC: {
        "entities": ["E32"],
        "status": "Current",
        "theme": "Electoral",
        "name": "London Assembly Constituencies",
        "full_name": "London Assembly Constituencies",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.LAD1961: {
        "entities": ["J04"],
        "status": "Current",
        "theme": "Census",
        "name": "1961 Census Districts",
        "full_name": "1961 Census Districts",
        "description": None,
        "countries": ["J"],
    },
    AreaTypeEnum.LAU1: {
        "entities": ["S30"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Local Administrative Units 1",
        "full_name": "Local Administrative Units 1",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.LAU2: {
        "entities": ["S31"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Local Administrative Units 2",
        "full_name": "Local Administrative Units 2",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.LAUA: {
        "entities": ["E06", "E07", "E08", "E09", "N09", "S12", "W06"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Local Authority",
        "full_name": "Local Authority District (LAD)/unitary authority (UA)/metropolitan district (MD)/London borough (LB)/ council area (CA)/district council area (DCA)",
        "description": "The current district/UA to which the postcode has been assigned. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["N", "W", "S", "E"],
    },
    AreaTypeEnum.LEP: {
        "entities": ["E37"],
        "status": "Current",
        "theme": "Other",
        "name": "Local Enterprise Partnership",
        "full_name": "Local Enterprise Partnership (LEP)",
        "description": "The primary LEP code for each English postcode. Pseudo codes are included for the rest of the UK. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["E"],
    },
    AreaTypeEnum.LEPNOP: {
        "entities": ["E53"],
        "status": "Current",
        "theme": "Other",
        "name": "LEP - non overlapping part ",
        "full_name": "LEP - non overlapping part ",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.LEPOP: {
        "entities": ["E52"],
        "status": "Current",
        "theme": "Other",
        "name": "LEP - overlapping part",
        "full_name": "LEP - overlapping part",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.LHB: {
        "entities": ["W11"],
        "status": "Current",
        "theme": "Health",
        "name": "Local Health Boards",
        "full_name": "Local Health Boards",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.LLSC: {
        "entities": ["E24"],
        "status": "Archived",
        "theme": "Other",
        "name": "Local Learning and Skills Council areas",
        "full_name": "Local Learning and Skills Council areas",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.LOC: {
        "entities": ["S19"],
        "status": "Current",
        "theme": "Other",
        "name": "Localities",
        "full_name": "Localities",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.LPA: {
        "entities": ["E60", "N13", "S44", "W43"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Local Planning Authorities",
        "full_name": "Local Planning Authorities",
        "description": None,
        "countries": ["N", "W", "S", "E"],
    },
    AreaTypeEnum.LRF: {
        "entities": ["E48", "W41"],
        "status": "Current",
        "theme": "Other",
        "name": "Local Resilience Forums",
        "full_name": "Local Resilience Forums",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.LSOA11: {
        "entities": ["E01", "S01", "W01"],
        "status": "Current",
        "theme": "Statistical Building Block",
        "name": "Lower Super Output Area",
        "full_name": "2011 Census Lower Layer Super Output Area (LSOA)/ Data Zone (DZ)/ SOA",
        "description": "The 2011 Census LSOA code for England and Wales, SOA code for Northern Ireland and DZ code for Scotland. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code. N.B. NI SOAs remain unchanged from 2001.",
        "countries": ["S", "W", "E"],
    },
    AreaTypeEnum.LSOA21: {
        "entities": ["E01", "S01", "W01"],
        "status": "Current",
        "theme": "Statistical Building Block",
        "name": "Lower Super Output Area",
        "full_name": "2021 Census Lower Layer Super Output Area (LSOA)/ Data Zone (DZ)/ SOA",
        "description": "The 2021 Census LSOA code for England and Wales, SOA code for Northern Ireland and DZ code for Scotland. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code. N.B. NI SOAs remain unchanged from 2001.",
        "countries": ["S", "W", "E"],
    },
    AreaTypeEnum.MCTY: {
        "entities": ["E11"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Metropolitan Counties",
        "full_name": "Metropolitan Counties",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.MSOA11: {
        "entities": ["E02", "S02", "W02"],
        "status": "Current",
        "theme": "Statistical Building Block",
        "name": "Middle Super Output Area",
        "full_name": "Middle Layer Super Output Area (MSOA)/Intermediate Zone (IZ)",
        "description": "The 2011 Census MSOA code for England and Wales and IZ code for Scotland. Pseudo codes are included for Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["S", "W", "E"],
    },
    AreaTypeEnum.MSOA21: {
        "entities": ["E02", "S02", "W02"],
        "status": "Current",
        "theme": "Statistical Building Block",
        "name": "Middle Super Output Area",
        "full_name": "Middle Layer Super Output Area (MSOA)/Intermediate Zone (IZ)",
        "description": "The 2021 Census MSOA code for England and Wales and IZ code for Scotland. Pseudo codes are included for Northern Ireland, Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["S", "W", "E"],
    },
    AreaTypeEnum.NAER: {
        "entities": ["W19"],
        "status": "Current",
        "theme": "Other",
        "name": "National Assembly Economic Regions",
        "full_name": "National Assembly Economic Regions",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.NAWC: {
        "entities": ["W09"],
        "status": "Current",
        "theme": "Electoral",
        "name": "National Assembly for Wales Constituencies",
        "full_name": "National Assembly for Wales Constituencies",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.NAWER: {
        "entities": ["W10"],
        "status": "Current",
        "theme": "Electoral",
        "name": "National Assembly for Wales Electoral Regions",
        "full_name": "National Assembly for Wales Electoral Regions",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.NCP: {
        "entities": ["E43"],
        "status": "Current",
        "theme": "Census",
        "name": "Non-Civil Parished Areas",
        "full_name": "Non-Civil Parished Areas",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.NCV: {
        "entities": ["E57"],
        "status": "Archived",
        "theme": "Health",
        "name": "National Cancer Vanguards",
        "full_name": "National Cancer Vanguards",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.NDC: {
        "entities": ["E27"],
        "status": "Archived",
        "theme": "Other",
        "name": "New Deal for Communities",
        "full_name": "New Deal for Communities",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.NHSER: {
        "entities": ["E40"],
        "status": "Current",
        "theme": "Health",
        "name": "NHS England Regions",
        "full_name": "NHS England Regions",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.NHSRLO: {
        "entities": ["E39"],
        "status": "Current",
        "theme": "Health",
        "name": "NHS England (Region, Local Office)",
        "full_name": "NHS England (Region, Local Office)",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.NIFRS: {
        "entities": ["N31"],
        "status": "Current",
        "theme": "Other",
        "name": "Northern Ireland Fire and Rescue Service",
        "full_name": "Northern Ireland Fire and Rescue Service",
        "description": None,
        "countries": ["N"],
    },
    AreaTypeEnum.NIFRSA: {
        "entities": ["N32"],
        "status": "Current",
        "theme": "Other",
        "name": "Northern Ireland Fire and Rescue Service Areas",
        "full_name": "Northern Ireland Fire and Rescue Service Areas",
        "description": None,
        "countries": ["N"],
    },
    AreaTypeEnum.NIFRSD: {
        "entities": ["N33"],
        "status": "Current",
        "theme": "Other",
        "name": "Northern Ireland Fire and Rescue Service Districts",
        "full_name": "Northern Ireland Fire and Rescue Service Districts",
        "description": None,
        "countries": ["N"],
    },
    AreaTypeEnum.NONCFA: {
        "entities": ["W34"],
        "status": "Current",
        "theme": "Other",
        "name": "Non-Communities First Areas",
        "full_name": "Non-Communities First Areas",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.NONNPARK: {
        "entities": ["W31"],
        "status": "Current",
        "theme": "Other",
        "name": "Non-National Park Area",
        "full_name": "Non-National Park Area",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.NONSRA: {
        "entities": ["W32"],
        "status": "Current",
        "theme": "Other",
        "name": "Non-Strategic Regeneration Area",
        "full_name": "Non-Strategic Regeneration Area",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.NPARK: {
        "entities": ["E26", "S21", "W18"],
        "status": "Current",
        "theme": "Other",
        "name": "National Parks",
        "full_name": "National Parks",
        "description": None,
        "countries": ["S", "W", "E"],
    },
    AreaTypeEnum.OA11: {
        "entities": ["E00", "N00", "S00", "W00"],
        "status": "Current",
        "theme": "Statistical Building Block",
        "name": "Output area",
        "full_name": "2011 Census Output Area (OA)/ Small Area (SA)",
        "description": "The 2011 Census OAs in GB and SAs in Northern Ireland were based on 2001 Census OAs, and they form the building bricks for defining higher level geographies. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no grid reference.",
        "countries": ["N", "W", "S", "E"],
    },
    AreaTypeEnum.OA21: {
        "entities": ["E00", "N00", "S00", "W00"],
        "status": "Current",
        "theme": "Statistical Building Block",
        "name": "Output area",
        "full_name": "2021 Census Output Area (OA)/ Small Area (SA)",
        "description": "The 2021 Census OAs in GB and SAs in Northern Ireland were based on 2001 Census OAs, and they form the building bricks for defining higher level geographies. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no grid reference.",
        "countries": ["N", "W", "S", "E"],
    },
    AreaTypeEnum.PAR: {
        "entities": ["E04"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Civil Parishes",
        "full_name": "Civil Parishes",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.PAR1961: {
        "entities": ["J02"],
        "status": "Current",
        "theme": "Census",
        "name": "1961 Census Parishes",
        "full_name": "1961 Census Parishes",
        "description": None,
        "countries": ["J"],
    },
    AreaTypeEnum.PCON: {
        "entities": ["E14", "N06", "S14", "W07"],
        "status": "Current",
        "theme": "Electoral",
        "name": "Westminster parliamentary constituency",
        "full_name": "Westminster parliamentary constituency",
        "description": "The Westminster parliamentary constituency code for each postcode. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["N", "W", "S", "E"],
    },
    AreaTypeEnum.PCT: {
        "entities": ["E16"],
        "status": "Archived",
        "theme": "Health",
        "name": "Primary Care Trust",
        "full_name": "Primary Care Trust (PCT)/ Care Trust/Care Trust Plus (CT)/ Local Health Board (LHB)/Community Health Partnership (CHP)/ Local Commissioning Group (LCG)/Primary Healthcare Directorate (PHD)",
        "description": "The code for the PCT/CT areas in England, LHBs in Wales, CHPs in Scotland, LCG in Northern Ireland and PHD in the Isle of Man. A pseudo code is included for Channel Islands. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["E"],
    },
    AreaTypeEnum.PFA: {
        "entities": ["E23", "N23", "S23", "W15"],
        "status": "Current",
        "theme": "Other",
        "name": "Police Force Area",
        "full_name": "Police Force Area (PFA)",
        "description": "The PFA code for each postcode. A single PFA covers each of Scotland and Northern Ireland (not coded). A pseudo code is included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["N", "W", "S", "E"],
    },
    AreaTypeEnum.PFD: {
        "entities": ["N24"],
        "status": "Current",
        "theme": "Other",
        "name": "Police Force Districts",
        "full_name": "Police Force Districts",
        "description": None,
        "countries": ["N"],
    },
    AreaTypeEnum.PHD: {
        "entities": ["M01"],
        "status": "Current",
        "theme": "Health",
        "name": "Primary Healthcare Directorate",
        "full_name": "Primary Healthcare Directorate",
        "description": None,
        "countries": ["M"],
    },
    AreaTypeEnum.PHEC: {
        "entities": ["E45"],
        "status": "Current",
        "theme": "Health",
        "name": "Public Health England Centres",
        "full_name": "Public Health England Centres",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.PHEREG: {
        "entities": ["E46"],
        "status": "Current",
        "theme": "Health",
        "name": "Public Health England Regions",
        "full_name": "Public Health England Regions",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.PSCREG: {
        "entities": ["W36"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Footprint Regions for Public Service Collaboration",
        "full_name": "Footprint Regions for Public Service Collaboration",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.PSHA: {
        "entities": ["E19"],
        "status": "Archived",
        "theme": "Health",
        "name": "Pan Strategic Health Authorities",
        "full_name": "Pan Strategic Health Authorities",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.PUA: {
        "entities": ["E25"],
        "status": "Current",
        "theme": "Other",
        "name": "Primary Urban Areas",
        "full_name": "Primary Urban Areas",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.REGD: {
        "entities": ["E28", "W20"],
        "status": "Current",
        "theme": "Other",
        "name": "Registration Districts",
        "full_name": "Registration Districts",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.REGSD: {
        "entities": ["E29", "W21"],
        "status": "Current",
        "theme": "Other",
        "name": "Registration Sub-district",
        "full_name": "Registration Sub-district",
        "description": None,
        "countries": ["W", "E"],
    },
    AreaTypeEnum.RGN: {
        "entities": ["E12"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Region",
        "full_name": "Region (former GOR)",
        "description": "The region code for each postcode. Pseudo codes are included for Wales, Scotland, Northern Ireland, Channel Island and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["E"],
    },
    AreaTypeEnum.ROAC: {
        "entities": ["S05"],
        "status": "Current",
        "theme": "Housing and Regeneration",
        "name": "Regeneration Outcome Areas - Community Planning Partnerships",
        "full_name": "Regeneration Outcome Areas - Community Planning Partnerships",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.ROAL: {
        "entities": ["S06"],
        "status": "Current",
        "theme": "Housing and Regeneration",
        "name": "Regeneration Outcome Areas - Local Areas",
        "full_name": "Regeneration Outcome Areas - Local Areas",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.ROAS: {
        "entities": ["S04"],
        "status": "Current",
        "theme": "Housing and Regeneration",
        "name": "Regeneration Outcome Agreement Areas - Scotland",
        "full_name": "Regeneration Outcome Agreement Areas - Scotland",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.RTP: {
        "entities": ["S07"],
        "status": "Current",
        "theme": "Transport",
        "name": "Regional Transport Partnerships",
        "full_name": "Regional Transport Partnerships",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SCN: {
        "entities": ["E55"],
        "status": "Current",
        "theme": "Health",
        "name": "Strategic Clinical Networks",
        "full_name": "Strategic Clinical Networks",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.SDPA: {
        "entities": ["S11"],
        "status": "Current",
        "theme": "Administrative",
        "name": "Strategic Development Plan Areas",
        "full_name": "Strategic Development Plan Areas",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SETT: {
        "entities": ["S20"],
        "status": "Current",
        "theme": "Other",
        "name": "Settlements",
        "full_name": "Settlements",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SETT2015: {
        "entities": ["N11"],
        "status": "Current",
        "theme": "Census",
        "name": "Settlement 2015",
        "full_name": "Settlement 2015",
        "description": None,
        "countries": ["N"],
    },
    AreaTypeEnum.SFRLSO: {
        "entities": ["S39"],
        "status": "Current",
        "theme": "Other",
        "name": "Scottish Fire and Rescue Local Senior Officer Areas",
        "full_name": "Scottish Fire and Rescue Local Senior Officer Areas",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SFRS: {
        "entities": ["S38"],
        "status": "Current",
        "theme": "Other",
        "name": "Scottish Fire and Rescue Service",
        "full_name": "Scottish Fire and Rescue Service",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SFRSDA: {
        "entities": ["S40"],
        "status": "Current",
        "theme": "Other",
        "name": "Scottish Fire and Rescue Service Delivery Areas",
        "full_name": "Scottish Fire and Rescue Service Delivery Areas",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SHA: {
        "entities": ["E18", "L00", "M00"],
        "status": "Current",
        "theme": "Health",
        "name": "Strategic Health Authorities",
        "full_name": "Strategic Health Authorities",
        "description": None,
        "countries": ["M", "E", "L"],
    },
    AreaTypeEnum.SLRP: {
        "entities": ["S42"],
        "status": "Current",
        "theme": "Other",
        "name": "Scottish Local Resilience Partnerships",
        "full_name": "Scottish Local Resilience Partnerships",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SMR: {
        "entities": ["S41"],
        "status": "Current",
        "theme": "Other",
        "name": "Scottish Marine Regions",
        "full_name": "Scottish Marine Regions",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SPA: {
        "entities": ["W23"],
        "status": "Current",
        "theme": "Other",
        "name": "Spatial Plan Areas",
        "full_name": "Spatial Plan Areas",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.SPC: {
        "entities": ["S16"],
        "status": "Current",
        "theme": "Electoral",
        "name": "Scottish Parliamentary Constituencies ",
        "full_name": "Scottish Parliamentary Constituencies ",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SPD: {
        "entities": ["S32"],
        "status": "Current",
        "theme": "Other",
        "name": "Scottish Police Divisions",
        "full_name": "Scottish Police Divisions",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SPR: {
        "entities": ["S17"],
        "status": "Current",
        "theme": "Electoral",
        "name": "Scottish Parliamentary Regions",
        "full_name": "Scottish Parliamentary Regions",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.SPSA: {
        "entities": ["W24"],
        "status": "Current",
        "theme": "Other",
        "name": "Spatial Plan Sub-areas",
        "full_name": "Spatial Plan Sub-areas",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.SRA: {
        "entities": ["W26"],
        "status": "Current",
        "theme": "Other",
        "name": "Strategic Regeneration Areas",
        "full_name": "Strategic Regeneration Areas",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.SRASUB: {
        "entities": ["W27"],
        "status": "Current",
        "theme": "Other",
        "name": "Strategic Regeneration Sub-areas",
        "full_name": "Strategic Regeneration Sub-areas",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.SRRP: {
        "entities": ["S43"],
        "status": "Current",
        "theme": "Other",
        "name": "Scottish Regional Resilience Partnerships",
        "full_name": "Scottish Regional Resilience Partnerships",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.TCA: {
        "entities": ["W28"],
        "status": "Current",
        "theme": "Other",
        "name": "Transport Consortia Areas",
        "full_name": "Transport Consortia Areas",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.TCITY: {
        "entities": ["J01"],
        "status": "Current",
        "theme": "Experimental",
        "name": "Major Towns and Cities",
        "full_name": "Major Towns and Cities",
        "description": None,
        "countries": ["J"],
    },
    AreaTypeEnum.TTWA: {
        "entities": ["E30", "K01", "N12", "S22", "W22"],
        "status": "Current",
        "theme": "Other",
        "name": "Travel to Work Area",
        "full_name": "Travel to Work Area (TTWA)",
        "description": "The TTWA code for the postcode. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["K", "E", "N", "S", "W"],
    },
    AreaTypeEnum.URC: {
        "entities": ["S10"],
        "status": "Current",
        "theme": "Economic",
        "name": "Urban Regeneration Companies",
        "full_name": "Urban Regeneration Companies",
        "description": None,
        "countries": ["S"],
    },
    AreaTypeEnum.USOA: {
        "entities": ["W03"],
        "status": "Current",
        "theme": "Statistical Building Block",
        "name": "Super Output Areas, Upper Layer",
        "full_name": "Super Output Areas, Upper Layer",
        "description": None,
        "countries": ["W"],
    },
    AreaTypeEnum.WA: {
        "entities": ["E50"],
        "status": "Current",
        "theme": "Other",
        "name": "Waste Authorities",
        "full_name": "Waste Authorities",
        "description": None,
        "countries": ["E"],
    },
    AreaTypeEnum.WARD: {
        "entities": ["E05", "N08", "S13", "W05"],
        "status": "Current",
        "theme": "Administrative/Electoral",
        "name": "Ward",
        "full_name": "(Electoral) ward/division",
        "description": "The current administrative/electoral area to which the postcode has been assigned. Pseudo codes are included for Channel Islands and Isle of Man. The field will otherwise be blank for postcodes with no OA code.",
        "countries": ["N", "W", "S", "E"],
    },
    AreaTypeEnum.WARD1961: {
        "entities": ["J03"],
        "status": "Current",
        "theme": "Census",
        "name": "1961 Census Wards",
        "full_name": "1961 Census Wards",
        "description": None,
        "countries": ["J"],
    },
    AreaTypeEnum.WZ11: {
        "entities": ["E33", "N19", "S34", "W35"],
        "status": "Current",
        "theme": "Census",
        "name": "Workplace Zone",
        "full_name": "2011 Census Workplace Zone",
        "description": "The UK WZ code. Pseudo codes are included for Channel Islands and Isle of Man. The field will be blank for UK postcodes with no grid reference.",
        "countries": ["N", "W", "S", "E"],
    },
}
