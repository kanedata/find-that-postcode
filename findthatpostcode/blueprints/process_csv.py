from __future__ import print_function

import csv
import io
from typing import Iterable

from elasticsearch import Elasticsearch

from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.utils import ESConfig

# List of potential postcode fields
POSTCODE_FIELDS = ["postcode", "postal_code", "post_code", "post code"]


def process_csv(
    csvfile: Iterable[str],
    outfile: io.IOBase,
    es: Elasticsearch,
    postcode_field: str = "postcode",
    fields: list[str] = ["lat", "long", "cty"],
    es_config: ESConfig | None = None,
) -> None:
    if not es_config:
        es_config = ESConfig(es_index="geo_postcode")

    # @TODO add option for different CSV dialects and for no headers
    # In the case of no headers you would find the field by number
    reader = csv.DictReader(csvfile)
    if not isinstance(reader.fieldnames, list):
        raise ValueError("CSV file must have headers")
    output_fields = reader.fieldnames + fields
    writer = csv.DictWriter(outfile, output_fields)
    writer.writeheader()
    code_cache = {"E99999999": "", "S99999999": "", "N99999999": "", "W99999999": ""}
    for _, row in enumerate(reader):
        for i in fields:
            row[i] = None
        postcode = Postcode.parse_id(row.get(postcode_field))
        if postcode:
            pc = es.get(
                index=es_config.es_index,
                doc_type=es_config.es_type,
                id=postcode,
                ignore=[404],  # type: ignore
            )
            if pc["found"]:
                for i in fields:
                    if i.endswith("_name"):
                        code = pc["_source"].get(i[:-5])
                        if code in code_cache:
                            row[i] = code_cache[code]
                        elif code:
                            area = es.get(
                                index="geo_area",
                                doc_type=es_config.es_type,
                                id=code,
                                ignore=[404],  # type: ignore
                                _source_excludes=["boundary"],  # type: ignore
                            )
                            if area["found"]:
                                row[i] = area["_source"].get("name")
                            else:
                                row[i] = code
                            code_cache[code] = row[i]
                        else:
                            row[i] = code
                    else:
                        row[i] = pc["_source"].get(i)
        writer.writerow(row)
