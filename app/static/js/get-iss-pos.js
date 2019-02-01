// Creo mappa con tutti i settaggi
var map = new L.Map('mapid').setView([0, 0], 2);
var url = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoic3RlZmFub2Zpc2MiLCJhIjoiY2pyNmt2bnBpMDBxaTQycHd4a2Z5OWVxdSJ9.evST_EkZDmx2IMrZzaU1Rw';
var attrib = 'Map data (c)OpenStreetMap contributors';
var osm = new L.TileLayer(url, {
    //minZoom: 8, 
    maxZoom: 8, 
    attribution: attrib, 
    id: 'mapbox.streets', 
    accessToken: 'pk.eyJ1Ijoic3RlZmFub2Zpc2MiLCJhIjoiY2pyNmt2bnBpMDBxaTQycHd4a2Z5OWVxdSJ9.evST_EkZDmx2IMrZzaU1Rw'
});
// Aggiungo il layer alla mappa
map.addLayer(osm);
//map.on('locationfound', onLocationfound);

// La classe SpaceIcon definisce tutte le caratteristiche comuni delle icone
var SpaceIcon = L.Icon.extend({
    options: {
        //shadowUrl: ,
        iconSize:     [38, 95],
        shadowSize:   [50, 64],
        iconAnchor:   [22, 94],
        shadowAnchor: [4, 62],
        popupAnchor:  [-3, -76]
    }
});
var issIcon = new SpaceIcon({iconUrl: '/static/img/satellite-60.png'})

var iss = null;
// Function che mostra un messaggio al passare del mouse sull'icona dell'oggetto tracciato
function popupOnMouseOver(marker,message){
    marker.bindPopup(message);
    marker.on('mouseover', function(e) {
        this.openPopup();
    });
    marker.on('mouseout', function(e){
        this.closePopup();
    });
}

// Determino la posizione del visitatore con delle ip-api
var observer_lat;
var observer_lng;
fetch('http://ip-api.com/json').then(response => {
    return response.json();
}).then(data => {
    observer_lat = data['lat'];
    observer_lng = data['lon'];
});

// Costruisco l'API per il tracking dell'oggetto identificato da un NORAD id
var noradId = document.getElementById("getpos").getAttribute("data-name");
var seconds = "2";
var observer_alt = "0";
var apiKey = "&apiKey=4MED2Z-GCCMV8-GPP7PZ-3XYW";
var apiRequest = "https://www.n2yo.com/rest/v1/satellite/positions/"+noradId+"/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/"+seconds+"/"+apiKey;

// Function che traccia con una linea rossa la traiettoria dell'oggetto identificata da un array di punti "positions"
function drawPolyline(map,positions){
    // create a red polyline from an array of LatLng points
    var latlngs = [];
    for (var i = 0; i < positions.length; i++){
        latlngs.push( [ positions[i].satlatitude, positions[i].satlongitude ] );
    }
    
    var polyline = L.polyline(latlngs, {color: 'red'}).addTo(map);
}

 // Traccio la traiettoria che l'oggetto percorrerà nei prossimi x=120 secondi
fetch("https://www.n2yo.com/rest/v1/satellite/positions/"+noradId+"/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/120/"+apiKey).then(response => {
    return response.json();
    }).then(data => {
    
        drawPolyline(map, data['positions']);
        
    }); 

 //Chiamo l'API per il tracking dell'oggetto, mostro il risultato sulla mappa
setInterval(function() {
    fetch(apiRequest).then(response => {
      return response.json();
      }).then(data => {
          if (iss != null){   // rimuovi la vecchia icona dell'oggetto
              map.removeLayer(iss);
          }
      
          var lat = data['positions'][0].satlatitude;
          var lng = data['positions'][0].satlongitude;
  
          iss = new L.marker([lat, lng], {icon: issIcon}).addTo(map);
          popupOnMouseOver(iss,"I am the " + data['info'].satname + "!" + "<br>" + "Lat: " + lat + "<br>" + "Lon: " + lng);
          drawPolyline(map, data['positions']);
          //map.setView([lat,lng], 2, {animation: true});
      
          });
  }, 5000); 
  /*
var i = -1;
var latitude = [];
var longitude = [];
// Chiamo l'API per il tracking dell'oggetto, mostro il risultato sulla mappa
setInterval(function() {
        if (i == -1 || i == 300) // è il primo passo o sono passati i 5 minuti, effettua un'altra API
        {
            fetch(apiRequest).then(response => {
                return response.json();
            }).then(data => {

                latitude = [];
                longitude = [];
                for (var x = 0; x < data['positions'].length; x++){ // prendi i nuovi dati
                    latitude.push(data['positions'][x].satlatitude);
                    longitude.push(data['positions'][x].satlongitude);
                }
                drawPolyline(map, data['positions']);   // Traccio la traiettoria che l'oggetto percorrerà nei prossimi 5 minuti

            });
            i = 0;
        }

        var lat = latitude[i];
        var lng = longitude[i];

        iss = new L.marker([lat, lng], {icon: issIcon}).addTo(map);
        popupOnMouseOver(iss,"I am the " + data['info'].satname + "!");
        
        map.setView([lat,lng], 3, {animation: true});
        i = i + 1;
        
}, 2000);
*/