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

- Countries: <https://opendata.arcgis.com/datasets/b789ba2f70fe45eb92402cee87092730_0.geojson>
- Westminster Parliamentary Constituencies: <https://opendata.arcgis.com/datasets/094f326b0b1247e3bcf1eb7236c24679_0.geojson>
- Counties and unitary authorities: <https://opendata.arcgis.com/datasets/0de4288db3774cb78e45b8b74e9eab31_0.geojson>
- Local Authority Districts: <https://opendata.arcgis.com/datasets/cec4f9cf783a47bab9295b2e513dd342_0.geojson>
- Regions: <https://opendata.arcgis.com/datasets/284d82f437554938b0d0fbb3c6522007_0.geojson>
- CCGs: <https://opendata.arcgis.com/datasets/c3398f0560844f74b76ca4b4136eb6a3_2.geojson>
- European electoral regions: <https://opendata.arcgis.com/datasets/20595dbf22534e20944c9cee42c665b3_0.geojson>
- Local Enterprise Partnerships: <https://opendata.arcgis.com/datasets/d4d519d1d1a1455a9b82331228f77489_2.geojson>
- NHS Commissioning Regions: <https://opendata.arcgis.com/datasets/edcbf58c70004d0f8d44501d07c38fe9_0.geojson>
- National Parks: <https://opendata.arcgis.com/datasets/f41bd8ff39ce4a2393c2f454006ea60a_0.geojson>
- Police Force areas: <https://opendata.arcgis.com/datasets/282af275c1a24c2ea64ff9e05bdd7d7d_0.geojson>
- Travel to Work Areas: <https://opendata.arcgis.com/datasets/d3062ec5f03b49a7be631d71586cac8c_2.geojson>
- Major Towns and Cities: <https://opendata.arcgis.com/datasets/58b0dfa605d5459b80bf08082999b27c_0.geojson>
- Combined Authorities: <https://opendata.arcgis.com/datasets/c6bd4568af5947519cf266b80a94de2e_0.geojson>

These files are large:

- Parishes (11,000): <https://opendata.arcgis.com/datasets/40b487621d814fcbb7c5ca8c816cb8ba_2.geojson> --code-field=par18cd
- Wards (8,900): <https://opendata.arcgis.com/datasets/d2dce556b4604be49382d363a7cade72_0.geojson>
- LSOAs (35,000): <https://opendata.arcgis.com/datasets/e993add3f1944437bc91ec7c76100c63_0.geojson>
- MSOAs (7,200): <https://opendata.arcgis.com/datasets/29fdaa2efced40378ce8173b411aeb0e_2.geojson>
- Built-up Areas (5,800): <https://opendata.arcgis.com/datasets/f6684981be23404e83321077306fa837_0.geojson>
- Built-up Area Sub-divisions (1,800): <https://opendata.arcgis.com/datasets/1f021bb824ee4820b353b4b58fab6df5_0.geojson>

Import the boundary files by running:

```bash
flask import boundaries "https://opendata.arcgis.com/datasets/094f326b0b1247e3bcf1eb7236c24679_0.geojson"
```

You can add more than one URL to each import script.

These imports will also take a while, and add significantly to the size of the
elasticsearch index. It may increase in size to over 5GB.

### 7. Import placenames (optional)

A further related dataset is placenames. The [ONS has a list of these](http://geoportal.statistics.gov.uk/datasets/a6c138d17ac54532b0ca8ee693922f10_0)
which can be imported using the `import placenames` command. An entry for each
placename is added to the `geo_placenames` elasticsearch index.

```bash
flask import placenames
```

The `--url` parameter can be used to customise the URL used.

### 7. Import statistics (optional)

Statistics can be added to areas, using ONS data. The available statistics are
added to LSOAs, but could also be added to other areas.

```bash
flask import imd2019
flask import imd2015
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
dokku config:set findthatpostcode FLASK_APP=findthatpostcode
dokku run findthatpostcode flask init-db
dokku run findthatpostcode flask import nspl
dokku run findthatpostcode flask import rgc
dokku run findthatpostcode flask import chd
dokku run findthatpostcode flask import msoanames
dokku run findthatpostcode flask import imd2019
dokku run findthatpostcode flask import imd2015
dokku run findthatpostcode flask import placenames

# import boundaries
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/7be6a3c1be3b4385951224d2f522470a_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/094f326b0b1247e3bcf1eb7236c24679_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/0de4288db3774cb78e45b8b74e9eab31_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/cec4f9cf783a47bab9295b2e513dd342_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/284d82f437554938b0d0fbb3c6522007_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/c3398f0560844f74b76ca4b4136eb6a3_2.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/20595dbf22534e20944c9cee42c665b3_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/d4d519d1d1a1455a9b82331228f77489_2.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/edcbf58c70004d0f8d44501d07c38fe9_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/f41bd8ff39ce4a2393c2f454006ea60a_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/282af275c1a24c2ea64ff9e05bdd7d7d_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/d3062ec5f03b49a7be631d71586cac8c_2.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/58b0dfa605d5459b80bf08082999b27c_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/c6bd4568af5947519cf266b80a94de2e_0.geojson

# large boundary files
dokku run findthatpostcode flask import boundaries --code-field=par18cd https://opendata.arcgis.com/datasets/40b487621d814fcbb7c5ca8c816cb8ba_2.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/d2dce556b4604be49382d363a7cade72_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/e993add3f1944437bc91ec7c76100c63_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/29fdaa2efced40378ce8173b411aeb0e_2.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/f6684981be23404e83321077306fa837_0.geojson
dokku run findthatpostcode flask import boundaries https://opendata.arcgis.com/datasets/1f021bb824ee4820b353b4b58fab6df5_0.geojson
```
