// https://github.com/jonshutt/Leaflet.OS.Graticule
L.OSGraticule = L.LayerGroup.extend({
    options: {
        interval: 1000,
        showLabels: true,
        redraw: 'move',
        maxZoom: 15,
        minZoom: 12,
        gridLetterStyle: "color: #216fff; font-size:12px;",
        lineColor: '#216fff',
        lineOpacity: 0.6,
        lineWeight: 1,
    },

    lineStyle: {
      stroke: true,
      color: '#216fff',
      opacity: 0.6,
      weight: 1,
      interactive: false,
      clickable: false //legacy support
    },


    initialize: function(options) {
        L.LayerGroup.prototype.initialize.call(this);
        L.Util.setOptions(this, options);
        this.lineStyle.color = this.options.lineColor;
        this.lineStyle.opacity = this.options.lineOpacity;
        this.lineStyle.weight = this.options.lineWeight;
    },

    onAdd: function(map) {
        this._map = map;
        var graticule = this.redraw();
        this._map.on('viewreset ' + this.options.redraw, graticule.redraw, graticule);
        this.eachLayer(map.addLayer, map);
    },

    onRemove: function(map) {
        map.off('viewreset '+ this.options.redraw, this.map);
        this.eachLayer(this.removeLayer, this);
    },

    hide: function() {
        this.options.hidden = true;
        this.redraw();
    },

    show: function() {
        this.options.hidden = false;
        this.redraw();
    },

    redraw: function() {
        this._bounds = this._map.getBounds().pad(0.5);

        this.clearLayers();

        var currentZoom = this._map.getZoom();

        if((currentZoom >= this.options.minZoom) && (currentZoom <= this.options.maxZoom)) {
          // get all corners
          this._bounds._northWest = {
            lat: this._bounds._northEast.lat,
            lng: this._bounds._southWest.lng
          }
          this._bounds._southEast = {
            lat: this._bounds._southWest.lat,
            lng: this._bounds._northEast.lng
          }

          //add OS points to all corners
          var NW = LatLongToOSGrid(this._bounds._northWest);
          this._bounds._northWest.easting = NW.easting;
          this._bounds._northWest.northing = NW.northing;

          var NE = LatLongToOSGrid(this._bounds._northEast);
          this._bounds._northEast.easting = NE.easting;
          this._bounds._northEast.northing = NE.northing;

          var SW = LatLongToOSGrid(this._bounds._southWest);
          this._bounds._southWest.easting = SW.easting;
          this._bounds._southWest.northing = SW.northing;

          var SE = LatLongToOSGrid(this._bounds._southEast);
          this._bounds._southEast.easting = SE.easting;
          this._bounds._southEast.northing = SE.northing;

          this.constructLines(this._bounds);

        }


        return this;
    },

    getOSMins: function() {
        //rounds up to nearest multiple of x
        var s = this.options.interval;
        return {
            easting: Math.floor(this._bounds._northWest.easting / s) * s,
            northing: Math.floor(this._bounds._northWest.northing / s) * s
        };
    },

    getOSLineCounts: function() {
      // console.log(this._bounds._northWest.easting, this._bounds._northEast.easting);
        var s = this.options.interval;
        return {
            x: Math.ceil((this._bounds._northEast.easting - this._bounds._northWest.easting) / s),
            y: Math.ceil((this._bounds._northWest.northing - this._bounds._southWest.northing) / s)
        };
    },

    constructLines: function(bounds) {

      var s = this.options.interval;

      var mins = this.getOSMins();
      var counts = this.getOSLineCounts();

      var lines = new Array();
      var labels = new Array();

      // // for vertical lines
      for (var i = 0; i <= counts.x; i++) {
        var e = mins.easting + (s * i);
        var n = mins.northing;
        var topLL = OSGridToLatLong(e, n);
        var bottomLL = OSGridToLatLong(e, n - (counts.y * s));
        var line = new L.Polyline([bottomLL, topLL], this.lineStyle);
        lines.push(line);

        if (this.options.showLabels) {
          labels.push(this.buildXLabel(topLL, gridrefNumToLet(e, n, 4).e));
        }
      }

      // for horizontal lines
      for (var i = 0; i <= counts.y; i++) {
        var e = mins.easting ;
        var n = mins.northing - (s * i);
        var leftLL = OSGridToLatLong(e, n);
        var rightLL = OSGridToLatLong(e + (counts.x * s) , n);
        var line = new L.Polyline([leftLL, rightLL], this.lineStyle);
        lines.push(line);

        if (this.options.showLabels) {
          labels.push(this.buildYLabel(leftLL, gridrefNumToLet(e, n, 4).n));
        }
      }

      lines.forEach(this.addLayer, this);
      labels.forEach(this.addLayer, this);

    },


    buildXLabel: function(pos, label) {
      var bounds = this._map.getBounds().pad(-0.001);
      pos.lat = bounds.getNorth();

      return L.marker(pos, {
        interactive: false,
        clickable: false, //legacy support
        icon: L.divIcon({
          iconSize: [0, 0],
          iconAnchor: [-10, 0],
          className: 'leaflet-grid-label',
          html: '<div style="'+ this.options.gridLetterStyle + '">' + label + '</div>'
        })
      });
    },

    buildYLabel: function(pos, label) {
      var bounds = this._map.getBounds().pad(-0.001);
      pos.lng = bounds.getWest();

      return L.marker(pos, {
        interactive: false,
        clickable: false, //legacy support
        icon: L.divIcon({
          iconSize: [0,0],
          iconAnchor: [-5,15],
          className: 'leaflet-grid-label',
          html: '<div style="'+ this.options.gridLetterStyle + '">' + label + '</div>'
        })
      });
    }



});

L.osGraticule = function(options) {
    return new L.OSGraticule(options);
};




function LatLongToOSGrid(p) {
  var lat = p.lat.toRad(), lon = p.lng.toRad();

  var a = 6377563.396, b = 6356256.910;          // Airy 1830 major & minor semi-axes
  var F0 = 0.9996012717;                         // NatGrid scale factor on central meridian
  var lat0 = (49).toRad(), lon0 = (-2).toRad();  // NatGrid true origin
  var N0 = -100000, E0 = 400000;                 // northing & easting of true origin, metres
  var e2 = 1 - (b*b)/(a*a);                      // eccentricity squared
  var n = (a-b)/(a+b), n2 = n*n, n3 = n*n*n;

  var cosLat = Math.cos(lat), sinLat = Math.sin(lat);
  var nu = a*F0/Math.sqrt(1-e2*sinLat*sinLat);              // transverse radius of curvature
  var rho = a*F0*(1-e2)/Math.pow(1-e2*sinLat*sinLat, 1.5);  // meridional radius of curvature
  var eta2 = nu/rho-1;

  var Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (lat-lat0);
  var Mb = (3*n + 3*n*n + (21/8)*n3) * Math.sin(lat-lat0) * Math.cos(lat+lat0);
  var Mc = ((15/8)*n2 + (15/8)*n3) * Math.sin(2*(lat-lat0)) * Math.cos(2*(lat+lat0));
  var Md = (35/24)*n3 * Math.sin(3*(lat-lat0)) * Math.cos(3*(lat+lat0));
  var M = b * F0 * (Ma - Mb + Mc - Md);              // meridional arc

  var cos3lat = cosLat*cosLat*cosLat;
  var cos5lat = cos3lat*cosLat*cosLat;
  var tan2lat = Math.tan(lat)*Math.tan(lat);
  var tan4lat = tan2lat*tan2lat;

  var I = M + N0;
  var II = (nu/2)*sinLat*cosLat;
  var III = (nu/24)*sinLat*cos3lat*(5-tan2lat+9*eta2);
  var IIIA = (nu/720)*sinLat*cos5lat*(61-58*tan2lat+tan4lat);
  var IV = nu*cosLat;
  var V = (nu/6)*cos3lat*(nu/rho-tan2lat);
  var VI = (nu/120) * cos5lat * (5 - 18*tan2lat + tan4lat + 14*eta2 - 58*tan2lat*eta2);

  var dLon = lon-lon0;
  var dLon2 = dLon*dLon, dLon3 = dLon2*dLon, dLon4 = dLon3*dLon, dLon5 = dLon4*dLon, dLon6 = dLon5*dLon;

  var N = I + II*dLon2 + III*dLon4 + IIIA*dLon6;
  var E = E0 + IV*dLon + V*dLon3 + VI*dLon5;

  return {
    letters: gridrefNumToLet(E, N, 6).full,
    easting: E,
    northing: N,
    lat: p.lat,
    lng: p.lng
  }
}



function OSGridToLatLong(E, N) {
  // var gr = gridrefLetToNum(gridRef);
  // var E = gr[0], N = gr[1];

  var a = 6377563.396, b = 6356256.910;              // Airy 1830 major & minor semi-axes
  var F0 = 0.9996012717;                             // NatGrid scale factor on central meridian
  var lat0 = 49*Math.PI/180, lon0 = -2*Math.PI/180;  // NatGrid true origin
  var N0 = -100000, E0 = 400000;                     // northing & easting of true origin, metres
  var e2 = 1 - (b*b)/(a*a);                          // eccentricity squared
  var n = (a-b)/(a+b), n2 = n*n, n3 = n*n*n;

  var lat=lat0, M=0;
  do {
    lat = (N-N0-M)/(a*F0) + lat;

    var Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (lat-lat0);
    var Mb = (3*n + 3*n*n + (21/8)*n3) * Math.sin(lat-lat0) * Math.cos(lat+lat0);
    var Mc = ((15/8)*n2 + (15/8)*n3) * Math.sin(2*(lat-lat0)) * Math.cos(2*(lat+lat0));
    var Md = (35/24)*n3 * Math.sin(3*(lat-lat0)) * Math.cos(3*(lat+lat0));
    M = b * F0 * (Ma - Mb + Mc - Md);                // meridional arc

  } while (N-N0-M >= 0.00001);  // ie until < 0.01mm

  var cosLat = Math.cos(lat), sinLat = Math.sin(lat);
  var nu = a*F0/Math.sqrt(1-e2*sinLat*sinLat);              // transverse radius of curvature
  var rho = a*F0*(1-e2)/Math.pow(1-e2*sinLat*sinLat, 1.5);  // meridional radius of curvature
  var eta2 = nu/rho-1;

  var tanLat = Math.tan(lat);
  var tan2lat = tanLat*tanLat, tan4lat = tan2lat*tan2lat, tan6lat = tan4lat*tan2lat;
  var secLat = 1/cosLat;
  var nu3 = nu*nu*nu, nu5 = nu3*nu*nu, nu7 = nu5*nu*nu;
  var VII = tanLat/(2*rho*nu);
  var VIII = tanLat/(24*rho*nu3)*(5+3*tan2lat+eta2-9*tan2lat*eta2);
  var IX = tanLat/(720*rho*nu5)*(61+90*tan2lat+45*tan4lat);
  var X = secLat/nu;
  var XI = secLat/(6*nu3)*(nu/rho+2*tan2lat);
  var XII = secLat/(120*nu5)*(5+28*tan2lat+24*tan4lat);
  var XIIA = secLat/(5040*nu7)*(61+662*tan2lat+1320*tan4lat+720*tan6lat);

  var dE = (E-E0), dE2 = dE*dE, dE3 = dE2*dE, dE4 = dE2*dE2, dE5 = dE3*dE2, dE6 = dE4*dE2, dE7 = dE5*dE2;
  lat = lat - VII*dE2 + VIII*dE4 - IX*dE6;
  var lon = lon0 + X*dE - XI*dE3 + XII*dE5 - XIIA*dE7;

  // return new LatLon(lat.toDeg(), lon.toDeg());
  return {
    lat: lat.toDeg(),
    lng: lon.toDeg()
  }
}


function gridrefNumToLet(e, n, digits) {
  // get the 100km-grid indices
  var e100k = Math.floor(e/100000), n100k = Math.floor(n/100000);

  if (e100k<0 || e100k>6 || n100k<0 || n100k>12) return '';

  // translate those into numeric equivalents of the grid letters
  var l1 = (19-n100k) - (19-n100k)%5 + Math.floor((e100k+10)/5);
  var l2 = (19-n100k)*5%25 + e100k%5;

  // compensate for skipped 'I' and build grid letter-pairs
  if (l1 > 7) l1++;
  if (l2 > 7) l2++;

  var let1 =  String.fromCharCode(l1+'A'.charCodeAt(0));
  var let2 =  String.fromCharCode(l2+'A'.charCodeAt(0));
  // var letPair = String.fromCharCode(l1+'A'.charCodeAt(0), l2+'A'.charCodeAt(0));
  letPair = let1 + let2;

  // strip 100km-grid indices from easting & northing, and reduce precision
  e = Math.floor((e%100000)/Math.pow(10,5-digits/2));
  n = Math.floor((n%100000)/Math.pow(10,5-digits/2));


  var gridRef = letPair + e.padLZ(digits/2) + n.padLZ(digits/2);

  // return gridRef;
  return {
    full: gridRef,
    let1: let1,
    let2: let2,
    e: e.padLZ(digits/2),
    n: n.padLZ(digits/2)
  }
}

Number.prototype.padLZ = function(w) {
var n = this.toString();
for (var i=0; i<w-n.length; i++) n = '0' + n;
return n;
}

/*
* extend Number object with methods for converting degrees/radians
*/
Number.prototype.toRad = function() {  // convert degrees to radians
  return this * Math.PI / 180;
}
Number.prototype.toDeg = function() {  // convert radians to degrees (signed)
  return this * 180 / Math.PI;
}
