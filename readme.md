Elasticsearch Postcodes
=======================

This project creates an elasticsearch index based on the UK postcode file, and
runs a webserver on top of it for making queries. It's like a more lightweight
version of [MapIt](https://mapit.mysociety.org.uk/).

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

- `/postcode/SW1A+1AA.html` gives information about a particular postcode.
- `/area/E09000033.html` gives information about an area, including example postcodes.
- `/area/search.html?q=Winchester` finds any areas containing a search query.
- `/areatype/laua.html` gives information about a type of area, including lists of
example codes.
- `/areatype.html` lists all the possible area types.
- `/point/53.490911,-2.095804.html` gives details of the postcode closest to the
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

- Configure host and port for elasticsearch index (and allow http url connections).
- Add area boundaries as geo-shapes in elasticsearch
- Find areas containing a point
