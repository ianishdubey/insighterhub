// irrigation.js

const BASE_URL = "http://127.0.0.1:8000/api/irrigation-areas/";
let chartInstance = null;

async function fetchIrrigationAreas() {
  try {
    const res = await fetch(BASE_URL, { headers: { 'Content-Type': 'application/json' } });
    if (!res.ok) return [];
    return await res.json();
  } catch (e) {
    console.error('Fetch irrigation areas failed', e);
    return [];
  }
}

async function initIrrigationMap() {
  mapInstance = L.map('map').setView([20.5937, 78.9629], 5);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapInstance);

  const irrigationAreas = await fetchIrrigationAreas();
  if (!irrigationAreas.length) return;

  // Color based on total irrigation area
  const getColorForArea = (totalArea) => {
    if (!totalArea || totalArea === 0) return '#9ca3af'; // Gray for no data
    if (totalArea < 50000) return '#10b981'; // Green for low
    if (totalArea < 500000) return '#f59e0b'; // Yellow for medium
    if (totalArea < 2000000) return '#f97316'; // Orange for high
    return '#ef4444'; // Red for very high
  };

  irrigationAreas.forEach(area => {
    if (area.latitude && area.longitude) {
      const color = getColorForArea(area.total_area);
      const marker = L.circleMarker([area.latitude, area.longitude], {
        radius: 8,
        color: color,
        fillColor: color,
        fillOpacity: 0.8,
        weight: 2
      }).addTo(mapInstance);
      
      const popupContent = `
        <div style="min-width: 250px;">
          <h4 style="margin: 0 0 8px 0; color: #2d3748;">${area.state}</h4>
          <p style="margin: 4px 0;"><strong>Total Irrigated Area:</strong> ${area.total_area ? area.total_area.toLocaleString() + ' Ha' : 'N/A'}</p>
          <p style="margin: 4px 0;"><strong>Kharif:</strong> ${area.kharif_area ? area.kharif_area.toLocaleString() + ' Ha' : 'N/A'}</p>
          <p style="margin: 4px 0;"><strong>Rabi:</strong> ${area.rabi_area ? area.rabi_area.toLocaleString() + ' Ha' : 'N/A'}</p>
          <p style="margin: 4px 0;"><strong>Perennial:</strong> ${area.perennial_area ? area.perennial_area.toLocaleString() + ' Ha' : 'N/A'}</p>
          <p style="margin: 4px 0;"><strong>Others:</strong> ${area.others_area ? area.others_area.toLocaleString() + ' Ha' : 'N/A'}</p>
        </div>
      `;
      
      marker.bindPopup(popupContent);
    }
  });

  const legend = L.control({ position: 'bottomright' });
  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'info legend');
    div.style.background = 'white';
    div.style.padding = '12px';
    div.style.borderRadius = '8px';
    div.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    div.style.fontSize = '12px';
    div.style.minWidth = '150px';
    
    const title = document.createElement('div');
    title.innerHTML = '<strong>Irrigation Area (Ha)</strong>';
    title.style.marginBottom = '8px';
    title.style.color = '#2d3748';
    div.appendChild(title);
    
    const legendItems = [
      { color: '#9ca3af', label: 'No Data' },
      { color: '#10b981', label: '< 50,000' },
      { color: '#f59e0b', label: '50,000 - 500,000' },
      { color: '#f97316', label: '500,000 - 2,000,000' },
      { color: '#ef4444', label: '> 2,000,000' }
    ];
    
    legendItems.forEach(({ color, label }) => {
      const item = document.createElement('div');
      item.style.marginBottom = '4px';
      item.innerHTML = `<span style="display:inline-block;width:12px;height:12px;background:${color};margin-right:8px;border-radius:50%;vertical-align:middle"></span>${label}`;
      div.appendChild(item);
    });
    return div;
  };
  legend.addTo(mapInstance);
}

async function initIrrigationChart() {
  const irrigationAreas = await fetchIrrigationAreas();
  if (!irrigationAreas.length) return;

  // Color based on total irrigation area
  const getColorForArea = (totalArea) => {
    if (!totalArea || totalArea === 0) return '#9ca3af'; // Gray for no data
    if (totalArea < 50000) return '#10b981'; // Green for low
    if (totalArea < 500000) return '#f59e0b'; // Yellow for medium
    if (totalArea < 2000000) return '#f97316'; // Orange for high
    return '#ef4444'; // Red for very high
  };

  const chartData = irrigationAreas
    .filter(area => area.latitude && area.longitude)
    .map(area => ({
      name: area.state,
      value: area.total_area || 0,
      color: getColorForArea(area.total_area)
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 15); // Show top 15 states

  const ctx = document.getElementById('irrigationChart').getContext('2d');
  
  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.map(d => d.name),
      datasets: [{
        label: 'Total Irrigated Area (ha)',
        data: chartData.map(d => d.value),
        backgroundColor: chartData.map(d => d.color),
        borderColor: chartData.map(d => d.color),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.parsed.y.toLocaleString()} ha`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Irrigated Area (hectares)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'States'
          }
        }
      }
    }
  });
}

// Map toggle functionality
let mapInstance = null;

function toggleMap() {
  const mapSection = document.getElementById('map-section');
  const chartSection = document.getElementById('chart-section');
  const toggleBtn = document.getElementById('toggle-map-btn');
  
  if (mapSection.style.display === 'none') {
    mapSection.style.display = 'block';
    chartSection.style.display = 'none';
    toggleBtn.textContent = '🗺️ Hide Map';
    toggleBtn.classList.add('active');
    document.getElementById('toggle-chart-btn').classList.remove('active');
    document.getElementById('toggle-chart-btn').textContent = '📊 Chart';
    
    // Initialize map if not already done
    if (!mapInstance) {
      initIrrigationMap();
    }
  } else {
    mapSection.style.display = 'none';
    toggleBtn.textContent = '🗺️ Map';
    toggleBtn.classList.remove('active');
  }
}

// Chart toggle functionality
function toggleChart() {
  const mapSection = document.getElementById('map-section');
  const chartSection = document.getElementById('chart-section');
  const toggleBtn = document.getElementById('toggle-chart-btn');
  
  if (chartSection.style.display === 'none') {
    chartSection.style.display = 'block';
    mapSection.style.display = 'none';
    toggleBtn.textContent = '📊 Hide Chart';
    toggleBtn.classList.add('active');
    document.getElementById('toggle-map-btn').classList.remove('active');
    document.getElementById('toggle-map-btn').textContent = '🗺️ Map';
    
    // Initialize chart if not already done
    if (!chartInstance) {
      initIrrigationChart();
    }
  } else {
    chartSection.style.display = 'none';
    toggleBtn.textContent = '📊 Chart';
    toggleBtn.classList.remove('active');
  }
}

// Table filtering functionality
function initTableFiltering() {
  const searchInput = document.getElementById('search-input');
  const sourceFilter = document.getElementById('source-filter');
  const seasonFilter = document.getElementById('season-filter');
  const table = document.querySelector('.land-table');
  const rows = table.querySelectorAll('tbody tr');

  function filterTable() {
    const searchTerm = searchInput.value.toLowerCase();
    const sourceValue = sourceFilter.value;
    const seasonValue = seasonFilter.value;

    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      const location = cells[1].textContent.toLowerCase();
      const source = cells[3].textContent;
      const season = cells[4].textContent;

      const matchesSearch = searchTerm === '' || 
        location.includes(searchTerm) || 
        source.toLowerCase().includes(searchTerm) || 
        season.toLowerCase().includes(searchTerm);

      const matchesSource = sourceValue === '' || source === sourceValue;
      const matchesSeason = seasonValue === '' || season === seasonValue;

      if (matchesSearch && matchesSource && matchesSeason) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }

  if (searchInput) searchInput.addEventListener('input', filterTable);
  if (sourceFilter) sourceFilter.addEventListener('change', filterTable);
  if (seasonFilter) seasonFilter.addEventListener('change', filterTable);
}

// Initialize trend charts
function initTrendCharts() {
  // Irrigation Coverage Chart
  const coverageCtx = document.getElementById('coverageChart');
  if (coverageCtx) {
    new Chart(coverageCtx, {
      type: 'line',
      data: {
        labels: ['2020', '2021', '2022', '2023', '2024', '2025'],
        datasets: [{
          label: 'Irrigation Coverage (%)',
          data: [65, 68, 72, 78, 82, 85],
          borderColor: '#4FC3F7',
          backgroundColor: 'rgba(79, 195, 247, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#ffffff'
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#ffffff'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          y: {
            ticks: {
              color: '#ffffff'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        }
      }
    });
  }

  // Water Use Efficiency Chart
  const efficiencyCtx = document.getElementById('efficiencyChart');
  if (efficiencyCtx) {
    new Chart(efficiencyCtx, {
      type: 'bar',
      data: {
        labels: ['2020', '2021', '2022', '2023', '2024', '2025'],
        datasets: [{
          label: 'Water Use Efficiency (%)',
          data: [65, 68, 72, 75, 78, 80],
          backgroundColor: 'rgba(76, 175, 80, 0.8)',
          borderColor: '#4CAF50',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#ffffff'
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#ffffff'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          y: {
            ticks: {
              color: '#ffffff'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        }
      }
    });
  }
}

// Update statistics with real data
async function updateStatistics() {
  const irrigationAreas = await fetchIrrigationAreas();
  if (!irrigationAreas.length) return;

  // Calculate totals
  const totalArea = irrigationAreas.reduce((sum, area) => sum + (area.total_area || 0), 0);
  const kharifArea = irrigationAreas.reduce((sum, area) => sum + (area.kharif_area || 0), 0);
  const rabiArea = irrigationAreas.reduce((sum, area) => sum + (area.rabi_area || 0), 0);
  const perennialArea = irrigationAreas.reduce((sum, area) => sum + (area.perennial_area || 0), 0);
  const othersArea = irrigationAreas.reduce((sum, area) => sum + (area.others_area || 0), 0);
  const statesCount = new Set(irrigationAreas.map(area => area.state)).size;

  // Update summary statistics
  document.getElementById('total-irrigated-area').textContent = totalArea.toLocaleString();
  document.getElementById('kharif-area').textContent = kharifArea.toLocaleString();
  document.getElementById('rabi-area').textContent = rabiArea.toLocaleString();
  document.getElementById('perennial-area').textContent = perennialArea.toLocaleString();

  // Update KPI cards
  document.getElementById('kpi-total-area').textContent = totalArea.toLocaleString() + ' Ha';
  document.getElementById('kpi-kharif-area').textContent = kharifArea.toLocaleString() + ' Ha';
  document.getElementById('kpi-rabi-area').textContent = rabiArea.toLocaleString() + ' Ha';
  document.getElementById('kpi-perennial-area').textContent = perennialArea.toLocaleString() + ' Ha';
  document.getElementById('kpi-others-area').textContent = othersArea.toLocaleString() + ' Ha';
  document.getElementById('kpi-states-count').textContent = statesCount;
}

// 🚪 Logout functionality
document.addEventListener('DOMContentLoaded', function() {
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login/";
    });
  }
  
  // Map toggle button
  const toggleMapBtn = document.getElementById("toggle-map-btn");
  if (toggleMapBtn) {
    toggleMapBtn.addEventListener("click", toggleMap);
  }
  
  // Chart toggle button
  const toggleChartBtn = document.getElementById("toggle-chart-btn");
  if (toggleChartBtn) {
    toggleChartBtn.addEventListener("click", toggleChart);
  }

  // Initialize table filtering
  initTableFiltering();
  
  // Initialize trend charts
  initTrendCharts();
  
  // Update statistics with real data
  updateStatistics();
});
