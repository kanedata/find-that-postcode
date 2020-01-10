Find that Postcode
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

You'll need to install the python `elasticsearch` and `flask` libraries, either
directly through `pip` or by running a virtual environment and running:

```bash
pip install -r requirements.txt
```

The code is written in python 3 and hasn't been tested in python 2.

### 3. Point flask to the app

Flask needs to know which app it's running. The easiest way to do this is to create
a file called `.env` in the project directory, and add the following contents:

```bash
FLASK_APP=findthatpostcode
FLASK_ENV=development
```

### 4. Create elasticsearch indexes

Run `flask init-db` to create the needed index and mappings
before data import.

### 5. Import postcodes

Run the following to import the data and save postcodes to the
elasticsearch index:

```bash
flask import nspl --url https://example.com/url-to-nspl
```

Replace `https://example.com/url-to-nspl` with the URL to the latest NSPL file.
This file can be found through a search on the [ONS Geoportal](https://geoportal.statistics.gov.uk/search?collection=Dataset&sort=-modified&tags=PRD_NSPL). On the page for the file copy the link shown in the
"Download" button on the right hand side.

This will then run the import process. It takes a while to run as there are over
2.5 million postcodes. The data will be around 1.3 GB in size on the disk.

### 6. Import area codes

Run the following to import the code history database and register of geographic codes.

```bash
flask import rgc
flask import chd
flask import msoanames # imports the names for MSOAs from House of Commons Library
```

The URL of the files used can be customised with the `--url` parameter. Unfortunately the 
ONS geoportal doesn't provide a persistent URL to the latest data.

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
- LSOAs: <https://opendata.arcgis.com/datasets/e993add3f1944437bc91ec7c76100c63_0.geojson>
- MSOAs: <http://geoportal.statistics.gov.uk/datasets/826dc85fb600440889480f4d9dbb1a24_2.geojson>
- Workplace Zones: <http://geoportal.statistics.gov.uk/datasets/a399c2a5922a4beaa080de63c0a218a3_2.geojson>
- Built-up Areas: <http://geoportal.statistics.gov.uk/datasets/278ff7af4efb4a599f70156e6e19cc9f_0.geojson>
- Built-up Area Sub-divisions: <http://geoportal.statistics.gov.uk/datasets/1f021bb824ee4820b353b4b58fab6df5_0.geojson>

Import the boundary files by running:

```bash
flask import boundaries "http://geoportal.statistics.gov.uk/datasets/ac17d33d37b94e48abd8ccbcde640dde_2.geojson"
```

You can add more than one URL to each import script.

These imports will also take a while, and add significantly to the size of the
elasticsearch index. It may increase in size to over 5GB.

### 7. Import placenames (optional)

A further related dataset is placenames. The [ONS has a list of these](http://geoportal.statistics.gov.uk/datasets/a6c138d17ac54532b0ca8ee693922f10_0)
which can be imported using the `import placenames` command. An entry for each
placename is added to the `geo_placenames` elasticsearch index.

```bash
python import placenames
```

The `--url` parameter can be used to customise the URL used.

### 7. Import statistics (optional)

Statistics can be added to areas, using ONS data. The available statistics are
added to LSOAs, but could also be added to other areas.

```bash
python import imd2019
python import imd2015
```

The `--url` parameter can be used to customise the URL used to get the data.

### Run tests

```bash
python -m pytest tests
```

Using the data
--------------

### Run the server

The project comes with a simple server (using the [flask](https://flask.palletsprojects.com/) framework) allowing
you to look at postcodes. The server returns either html pages (using `.html`)
or json data by default.

Run the server by:

```bash
flask run
```

By default the server is available at <http://localhost:5000/>.

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
curl "http://localhost:9200/geo_postcode/_doc/SW1A+1AA?pretty"
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
    "rgn": "E12000007",
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
curl "http://localhost:9200/geo_area/_doc/E00046056?pretty"
```

```json
{
  "_index": "postcode",
  "_type": "code",
  "_id": "E00046056",
  "_version": 2,
  "found": true,
  "_source": {
    "code": "E00046056",
    "name": "",
    "name_welsh": null,
    "statutory_instrument_id": "1111/1001",
    "statutory_instrument_title": "GSS re-coding strategy",
    "date_start": "2009-01-01T00:00:00",
    "date_end": null,
    "parent": "E01009081",
    "entity": "E00",
    "owner": "ONS",
    "active": true,
    "areaehect": 3.75,
    "areachect": 3.75,
    "areaihect": 0,
    "arealhect": 3.75,
    "sort_order": "E00046056",
    "predecessor": [
        "00CNFN0006"
    ],
    "successor": [],
    "equivalents": {
        "ons": "00CNFN0006"
    }
  }
}
```

Todo / future features
----------------------

- Find areas containing a point


Dokku setup
----------

```bash
# create app
dokku apps:create findthatpostcode

# add permanent data storage
dokku storage:mount findthatpostcode /var/lib/dokku/data/storage/findthatpostcode:/data

# enable domain
dokku domains:enable findthatpostcode
dokku domains:add findthatpostcode postcodes.findthatcharity.uk

# elasticsearch
sudo dokku plugin:install https://github.com/dokku/dokku-elasticsearch.git elasticsearch
dokku elasticsearch:create findthatpostcode-es
dokku elasticsearch:link findthatpostcode-es findthatpostcode

# SSL
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku config:set --no-restart findthatpostcode DOKKU_LETSENCRYPT_EMAIL=your@email.tld
dokku letsencrypt findthatpostcode
dokku letsencrypt:cron-job --add
```

### 2. Add as a git remote and push

On local machine:

```bash
git remote add dokku dokku@SERVER_HOST:findthatpostcode
git push dokku master
```

### 3. Setup and run import

On Dokku server run:

```bash
# setup and run import
dokku run findthatpostcode flask init-db
dokku run findthatpostcode flask import nspl
dokku run findthatpostcode flask import rgc
dokku run findthatpostcode flask import chd
dokku run findthatpostcode flask import msoanames
dokku run findthatpostcode flask import boundaries http://geoportal.statistics.gov.uk/datasets/37bcb9c9e788497ea4f80543fd14c0a7_2.geojson http://geoportal.statistics.gov.uk/datasets/deeb99fdf09949bc8ed4dc95c80da279_2.geojson http://geoportal.statistics.gov.uk/datasets/687f346f5023410ba86615655ff33ca9_2.geojson http://geoportal.statistics.gov.uk/datasets/686603e943f948acaa13fb5d2b0f1275_2.geojson http://geoportal.statistics.gov.uk/datasets/f99b145881724e15a04a8a113544dfc5_2.geojson http://geoportal.statistics.gov.uk/datasets/ac17d33d37b94e48abd8ccbcde640dde_2.geojson http://geoportal.statistics.gov.uk/datasets/44667328cf45481ba91aef2f646b5fc0_2.geojson http://geoportal.statistics.gov.uk/datasets/532e3bb99acf44549ebb882c15646059_2.geojson http://geoportal.statistics.gov.uk/datasets/b804b37c78004e788becf75f712f6a38_2.geojson http://geoportal.statistics.gov.uk/datasets/6e93e6b47edd49ab827a1831d8eb0f57_2.geojson http://geoportal.statistics.gov.uk/datasets/df607d4ffa124cdca8317e3e63d45d78_2.geojson http://geoportal.statistics.gov.uk/datasets/3e5a096a8c7c456fb6d3164a3f44b005_2.geojson http://geoportal.statistics.gov.uk/datasets/7ddabffc9b46444bbf548732642f1ea2_2.geojson http://geoportal.statistics.gov.uk/datasets/d3062ec5f03b49a7be631d71586cac8c_2.geojson
dokku run findthatpostcode flask import boundaries http://geoportal.statistics.gov.uk/datasets/f13dad37854b4a1f869bf178489ff99a_2.geojson
dokku run findthatpostcode flask import boundaries http://geoportal.statistics.gov.uk/datasets/afcc88affe5f450e9c03970b237a7999_2.geojson
dokku run findthatpostcode flask import boundaries http://geoportal.statistics.gov.uk/datasets/da831f80764346889837c72508f046fa_2.geojson
dokku run findthatpostcode flask import boundaries http://geoportal.statistics.gov.uk/datasets/826dc85fb600440889480f4d9dbb1a24_2.geojson
dokku run findthatpostcode flask import boundaries http://geoportal.statistics.gov.uk/datasets/a399c2a5922a4beaa080de63c0a218a3_2.geojson
dokku run findthatpostcode flask import boundaries http://geoportal.statistics.gov.uk/datasets/278ff7af4efb4a599f70156e6e19cc9f_0.geojson
dokku run findthatpostcode flask import boundaries http://geoportal.statistics.gov.uk/datasets/1f021bb824ee4820b353b4b58fab6df5_0.geojson
```
