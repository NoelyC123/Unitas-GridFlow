const map = L.map('map').setView([50.1, 10.1], 10);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

fetch('/map_data')
  .then(res => res.json())
  .then(data => {
    L.geoJSON(data, {
      pointToLayer: (feature, latlng) => {
        const status = feature.properties.qa_status;
        const fillColor = status === "PASS" ? "#28a745" :
                          status === "FAIL" ? "#dc3545" : "#888";

        return L.circleMarker(latlng, {
          radius: 8,
          fillColor: fillColor,
          color: "#222",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.9
        }).bindPopup(formatPopup(feature.properties));
      }
    }).addTo(map);
  });

function formatPopup(props) {
  let html = `<b>${props.name}</b><br>ID: ${props.id}<br>Status: ${props.qa_status}`;
  if (props.qa_status === "FAIL") {
    html += `<br><b>Issues:</b><ul>`;
    props.qa_issues.split("; ").forEach(issue => {
      html += `<li>${issue}</li>`;
    });
    html += `</ul>`;
  }
  return html;
}
