const UK_BOUNDS = [
    [60.86, 1.76],
    [49.86, -8.65]
]
var center = [53.825564, -2.421976];
if (window.postcodes && postcodes.length > 0) {
    center = [postcodes[0]["lat"], postcodes[0]["lon"]];
}

var mymap = L.map('postcode-map', {
    zoomSnap: 0.1
}).setView(center, 9);
var layer = new L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> <a href="https://www.stamen.com/" target="_blank">&copy; Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/about" target="_blank">OpenStreetMap</a> contributors',
}).addTo(mymap);
L.osGraticule({ showLabels: false, lineColor: '#ddd' }).addTo(mymap);

var location_map = null;
if (document.getElementById('location-map')) {
    location_map = L.map('location-map', {
        zoomControl: false,
        attributionControl: false,
        boxZoom: false,
        doubleClickZoom: false,
        dragging: false,
        scrollWheelZoom: false,
    });
    new L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> <a href="https://www.stamen.com/" target="_blank">&copy; Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/about" target="_blank">OpenStreetMap</a> contributors',
    }).addTo(location_map);
    location_map.fitBounds(UK_BOUNDS);
    location_map.setMinZoom(location_map.getZoom());
    location_map.setMaxZoom(location_map.getZoom());
}

if (window.postcodes) {
    var markers = L.featureGroup();
    for (const postcode of postcodes) {
        var marker = L.circleMarker([postcode['lat'], postcode['lon']], {
            radius: 5,
            fillOpacity: 0.8
        }).addTo(markers);
        // marker.bindPopup(
        //     "<a href=\"/postcodes/{{ postcode.id }}.html\">{{ postcode.id }}</a>",
        //     {
        //         autoClose: false
        //     }
        // ).openPopup();
    }
}

var postcode_show = function () {
    if ("show_postcode" in window && show_postcode) {
        markers.addTo(mymap);
    }
}

if (geojson) {
    fetch(geojson)
        .then(function (response) {
            if (response.status !== 200) {
                throw new Error("Not 200 response")
            } else {
                return response.json();
            }
        })
        .then(function (geojson) {
            var boundary_json = L.geoJSON(geojson, {
                invert: geojson.features.length == 1,
                style: {
                    stroke: true,
                    color: '#00449e',
                    weight: 3,
                    fill: true,
                    fillColor: (geojson.features.length == 1 ? '#fff' : '#00449e'),
                    fillOpacity: (geojson.features.length == 1 ? 0.8 : 0.2)
                },
                onEachFeature: (feature, layer) => {
                    layer.bindTooltip(
                        feature.properties.name + " (" + feature.properties.code + ")",
                        {
                            permanent: true,
                            direction: 'center',
                            className: 'countryLabel'
                        }
                    );
                }
            });
            boundary_json.addTo(mymap);
            postcode_show();
            mymap.fitBounds(boundary_json.getBounds());

            if (location_map) {
                boundary_json.eachLayer((layer) => {
                    L.marker(layer.getBounds().getCenter()).addTo(location_map);
                });
            }

            // if(typeof parent_geojson !== 'undefined'){
            //     fetch(parent_geojson)
            //         .then(function (response) {
            //             if (response.status !== 200) {
            //                 throw new Error("Not 200 response")
            //             } else {
            //                 return response.json();
            //             }
            //         })
            //         .then(function (geojson) {
            //             var parent_geojson = L.geoJSON(geojson, {
            //                 style: {
            //                     stroke: true,
            //                     color: '#00449e99',
            //                     weight: 1,
            //                     fill: false,
            //                 },
            //             });
            //             parent_geojson.addTo(mymap);
            //             mymap.fitBounds(parent_geojson.getBounds());
            //         });

            // }

        })
        .catch((error) => {
            postcode_show();
            mymap.fitBounds(markers.getBounds());
            console.log(error);
        });
} else {
    postcode_show();
    mymap.fitBounds(markers.getBounds());
}