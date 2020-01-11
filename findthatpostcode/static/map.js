
var center = [53.825564, -2.421976];
if(postcodes.length > 0){
    center = [postcodes[0]["lat"], postcodes[0]["lon"]];
}

var mymap = L.map('postcode-map', {
    zoomSnap: 0.1
}).setView(center, 9);
var layer = new L.StamenTileLayer("toner").addTo(mymap);
L.osGraticule({ showLabels: false, lineColor: '#ddd' }).addTo(mymap);

var markers = L.featureGroup();
for (const postcode of postcodes){
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

var postcode_show = function () {
    if ("show_postcode" in window && show_postcode) {
        markers.addTo(mymap);
    }
}

if(geojson){
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
                invert: true,
                style: {
                    stroke: true,
                    color: '#00449e',
                    weight: 3,
                    fill: true,
                    fillColor: '#fff',
                    fillOpacity: 0.95
                }
            });
            boundary_json.addTo(mymap);
            postcode_show();
            mymap.fitBounds(boundary_json.getBounds());
        })
        .catch((error) => {
            postcode_show();
            mymap.fitBounds(markers.getBounds());
        });
} else {
    postcode_show();
    mymap.fitBounds(markers.getBounds());
}