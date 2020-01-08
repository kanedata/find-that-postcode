
var mymap = L.map('postcode-map', {
    zoomSnap: 0.1
}).setView(
    [postcodes[0]["lat"], postcodes[0]["lon"]],
    9
);
var layer = new L.StamenTileLayer("toner").addTo(mymap);
// L.osGraticule({ showLabels: false, lineColor: '#ddd' }).addTo(mymap);

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
// markers.addTo(mymap);
// mymap.fitBounds(markers.getBounds());
fetch(geojson)
    .then(function (response) {
        return response.json();
    }).then(function (geojson) {
        var boundary_json = L.geoJSON(geojson, {
            invert: true,
            style: {
                stroke: true,
                weight: 2,
                fill: true,
                fillColor: '#fff',
                fillOpacity: 0.9
            }
        });
        boundary_json.addTo(mymap);
        mymap.fitBounds(boundary_json.getBounds());
    });