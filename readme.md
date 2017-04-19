Elasticsearch Postcodes
=======================

This project creates an elasticsearch index based on the UK postcode file, and
runs a webserver on top of it for making queries. It's like a more lightweight
and less sophisticated version of [MapIt](https://mapit.mysociety.org.uk/).

Setup
-----

### 1. Setup elasticsearch

[Follow the instructions](https://www.elastic.co/downloads/elasticsearch) to
download and install elasticsearch.

Run the server. At the moment the scripts only work on a default server of
`localhost:9200` but a future version will have configurable host and port.

### 2. Install python dependencies

You'll need to install the python `elasticsearch` and `bottle` libraries, either
directly through `pip` or by running a virtual environment and running:

```bash
pip install -r requirements.txt
```

The code is written in python 3 and hasn't been tested in python 2.

### 3. Create elasticsearch indexes

Run `python create_elasticsearch.py` to create the needed index and mappings
before data import.

### 4. Download NSPL files

[Download the latest National Statistics Postcode Library](http://ons.maps.arcgis.com/home/item.html?id=a26683d2393743f4b87c89141cd1b2e8)
file from the ONS geography site. Unfortunately there isn't a way to directly
link to the latest file, it needs to be manually downloaded.

This file can be stored anywhere but it may make sense to put it in a `data/`
folder under this directory.

### 5. Import postcodes and codes

Run the following to import the data and save postcodes and codes to the
elasticsearch index:

```bash
python import_postcodes.py data/NSPL_FEB_2017_UK.zip
```

Replace `data/NSPL_FEB_2017_UK.zip` with the relative or absolute path to the
file downloaded above.

This will then run the import process. It takes a while to run as there are over
2.5 million postcodes. The data will be around 1.3 GB in size on the disk.

### 6. Import boundaries (optional)

Boundary files can be found on the [ONS Geoportal](http://geoportal.statistics.gov.uk/datasets?q=Latest_Boundaries&sort_by=name&sort_order=asc).
Generally the "Generalised Clipped" versions should be used to minimise the file
size. Open each boundary file link and find the "API" link on the right hand
side, and copy the `GeoJSON` link, or download the file.

These files are the latest available at April 2017:

- Countries: <http://geoportal.statistics.gov.uk/datasets/37bcb9c9e788497ea4f80543fd14c0a7_2.geojson>
- Westminster Parliamentary Constituencies: <http://geoportal.statistics.gov.uk/datasets/deeb99fdf09949bc8ed4dc95c80da279_2.geojson>
- Counties and unitary authorities: <http://geoportal.statistics.gov.uk/datasets/687f346f5023410ba86615655ff33ca9_2.geojson>
- Local Authority Districts: <http://geoportal.statistics.gov.uk/datasets/686603e943f948acaa13fb5d2b0f1275_2.geojson>
- Regions: <http://geoportal.statistics.gov.uk/datasets/f99b145881724e15a04a8a113544dfc5_2.geojson>
- CCGs: <http://geoportal.statistics.gov.uk/datasets/ac17d33d37b94e48abd8ccbcde640dde_2.geojson>
- European electoral regions: <http://geoportal.statistics.gov.uk/datasets/44667328cf45481ba91aef2f646b5fc0_2.geojson>
- Local Enterprise Partnerships: <http://geoportal.statistics.gov.uk/datasets/532e3bb99acf44549ebb882c15646059_2.geojson>
- NHS Commissioning Regions: <http://geoportal.statistics.gov.uk/datasets/b804b37c78004e788becf75f712f6a38_2.geojson>
- NHS England Regions: <http://geoportal.statistics.gov.uk/datasets/6e93e6b47edd49ab827a1831d8eb0f57_2.geojson>
- National Parks: <http://geoportal.statistics.gov.uk/datasets/df607d4ffa124cdca8317e3e63d45d78_2.geojson>
- Police Force areas: <http://geoportal.statistics.gov.uk/datasets/3e5a096a8c7c456fb6d3164a3f44b005_2.geojson>
- Strategic Clinical Networks: <http://geoportal.statistics.gov.uk/datasets/7ddabffc9b46444bbf548732642f1ea2_2.geojson>
- Travel to Work Areas: <http://geoportal.statistics.gov.uk/datasets/d3062ec5f03b49a7be631d71586cac8c_2.geojson>

These files are large:

- Parishes: <http://geoportal.statistics.gov.uk/datasets/f13dad37854b4a1f869bf178489ff99a_2.geojson>
- Wards: <http://geoportal.statistics.gov.uk/datasets/afcc88affe5f450e9c03970b237a7999_2.geojson>
- LSOAs: <http://geoportal.statistics.gov.uk/datasets/da831f80764346889837c72508f046fa_2.geojson>
- MSOAs: <http://geoportal.statistics.gov.uk/datasets/826dc85fb600440889480f4d9dbb1a24_2.geojson>
- Workplace Zones: <http://geoportal.statistics.gov.uk/datasets/a399c2a5922a4beaa080de63c0a218a3_2.geojson>
- Built-up Areas: <http://geoportal.statistics.gov.uk/datasets/278ff7af4efb4a599f70156e6e19cc9f_0.geojson>
- Built-up Area Sub-divisions: <http://geoportal.statistics.gov.uk/datasets/1f021bb824ee4820b353b4b58fab6df5_0.geojson>

Import the boundary files by running:

```bash
python import_boundaries.py "http://geoportal.statistics.gov.uk/datasets/ac17d33d37b94e48abd8ccbcde640dde_2.geojson"
```

These imports will also take a while, and add significantly to the size of the
elasticsearch index. It may increase in size to over 5GB.

### 7. Import placenames (optional)

A further related dataset is placenames. The [ONS has a list of these](http://geoportal.statistics.gov.uk/datasets/a6c138d17ac54532b0ca8ee693922f10_0)
which can be imported using the `import_placenames.py` script. An entry for each
placename is added to the `postcode/placenames` elasticsearch index/type.

To use, first download the [placenames CSV file from ONS](http://geoportal.statistics.gov.uk/datasets/a6c138d17ac54532b0ca8ee693922f10_0),
and then run:

```bash
python import_placenames.py "path/to/file.csv"
```

### Run tests

```bash
python -m pytest
```

Using the data
--------------

### Run the server

The project comes with a simple server (using the [bottle]() framework) allowing
you to look at postcodes. The server returns either html pages (using `.html`)
or json data by default.

Run the server by:

```bash
python server.py
```

By default the server is available at <http://localhost:8080/>.

#### Server endpoints

The server has a number of possible uses:

- `/postcodes/SW1A+1AA.html` gives information about a particular postcode.
- `/areas/E09000033.html` gives information about an area, including example postcodes.
- `/areas/search.html?q=Winchester` finds any areas containing a search query.
- `/areatypes/laua.html` gives information about a type of area, including lists of
example codes.
- `/areatypes.html` lists all the possible area types.
- `/points/53.490911,-2.095804.html` gives details of the postcode closest to the
  latitude, longitude point. If it's more than 10km from the nearest postcode it's
  assumed to be outside the UK.

### Elasticsearch REST api

The data is also now available in an elasticsearch index to be used in other local
applications using the elasticsearch REST api.

#### Find details on a postcode

```bash
curl "http://localhost:9200/postcode/postcode/SW1A+1AA?pretty"
```

```json
{
  "_index": "postcode",
  "_type": "postcode",
  "_id": "SW1A 1AA",
  "_version": 1,
  "found": true,
  "_source": {
    "bua11": "E34004707",
    "oac11": "2C3",
    "park": "E99999999",
    "osnrth1m": 179645,
    "buasd11": "E35000546",
    "lsoa11": "E01004736",
    "pcon": "E14000639",
    "pct": "E16000057",
    "nuts": "E05000644",
    "pcds": "SW1A 1AA",
    "ccg": "E38000031",
    "osgrdind": 1,
    "eer": "E15000007",
    "hlthau": "E18000007",
    "imd": 16419,
    "ward": "E05000644",
    "wz11": "E33031119",
    "ctry": "E92000001",
    "oseast1m": 529090,
    "pcd2": "SW1A 1AA",
    "laua": "E09000033",
    "gor": "E12000007",
    "location": {
      "lon": -0.141588,
      "lat": 51.501009
    },
    "lat": 51.501009,
    "usertype": 1,
    "cty": "E99999999",
    "ttwa": "E30000234",
    "lep1": "E37000023",
    "pcd": "SW1A1AA",
    "teclec": "E24000014",
    "dointr": "1980-01-01T00:00:00",
    "oa11": "E00023938",
    "long": -0.141588,
    "pfa": "E23000001",
    "ru11ind": "A1",
    "hro": "E19000003",
    "msoa11": "E02000977",
    "lep2": null,
    "doterm": null
  }
}
```

#### Find details on an area

```bash
curl "http://localhost:9200/postcode/code/E14000639?pretty"
```

```json
{
  "_index": "postcode",
  "_type": "code",
  "_id": "E14000639",
  "_version": 2,
  "found": true,
  "_source": {
    "PCON14CD": "E14000639",
    "name": "Cities of London and Westminster",
    "PCON14NM": "Cities of London and Westminster",
    "type": "pcon",
    "name_welsh": "Cities of London and Westminster"
  }
}
```

Todo / future features
----------------------

- Find areas containing a point
