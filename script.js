let map = L.map('map').setView([33.5899, -7.6039], 13);
let geojsonLayer = null;

L.tileLayer('https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
  maxZoom: 20
}).addTo(map);

// Charger et afficher le GeoJSON
fetch('data/Casablanca.geojson')
  .then(res => res.json())
  .then(data => {
    geojsonLayer = L.geoJSON(data, {
      style: { color: 'green', weight: 2 },
      onEachFeature: function (feature, layer) {
        const titre = feature.properties.num || 'Inconnu';
        layer.bindPopup(`Titre : ${titre}`);
        layer._titre = titre; // Stockage personnalisé
      }
    }).addTo(map);
  })
  .catch(err => console.error('Erreur chargement GeoJSON:', err));

// Recherche par numéro
function rechercherTitre() {
  const val = document.getElementById("search").value.trim().toUpperCase();
  if (!geojsonLayer) return;

  geojsonLayer.eachLayer(layer => {
    if (layer._titre.toUpperCase() === val) {
      map.fitBounds(layer.getBounds(), { padding: [20, 20] });
      layer.openPopup();
    }
  });
}
