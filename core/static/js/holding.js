// holding.js

const BASE_URL = "http://127.0.0.1:8000/api/regions/";

async function fetchRegions() {
  try {
    const res = await fetch(BASE_URL, { headers: { 'Content-Type': 'application/json' } });
    if (!res.ok) return [];
    return await res.json();
  } catch (e) {
    console.error('Fetch regions failed', e);
    return [];
  }
}

let mapInstance = null;
let chartInstance = null;

async function initHoldingMap() {
  mapInstance = L.map('map').setView([20.5937, 78.9629], 5);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapInstance);

  const regions = await fetchRegions();
  if (!regions.length) return;

  const values = regions
    .map(r => r.land_holding ?? r.average_land_holding)
    .filter(v => typeof v === 'number' && !isNaN(v))
    .sort((a,b) => a-b);
  const q = (p) => values.length ? values[Math.floor((values.length-1)*p)] : undefined;
  const q1 = q(0.25), q2 = q(0.5), q3 = q(0.75);

  const colorFor = (v) => {
    if (v == null) return '#9ca3af';
    if (q1 == null || q2 == null || q3 == null) return '#3b82f6';
    if (v <= q1) return '#a7f3d0';
    if (v <= q2) return '#34d399';
    if (v <= q3) return '#10b981';
    return '#047857';
  };

  regions.forEach(r => {
    if (r.latitude && r.longitude) {
      const lh = r.land_holding ?? r.average_land_holding;
      const marker = L.circleMarker([r.latitude, r.longitude], {
        radius: 7,
        color: colorFor(lh),
        fillColor: colorFor(lh),
        fillOpacity: 0.9,
        weight: 1
      }).addTo(mapInstance);
      marker.bindPopup(`<b>${r.name}</b><br>Land Holding: ${lh ?? 'N/A'} ha`);
    }
  });

  const legend = L.control({ position: 'bottomright' });
  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'info legend');
    const grades = ['<= Q1', 'Q1–Q2', 'Q2–Q3', '> Q3'];
    const colors = ['#a7f3d0', '#34d399', '#10b981', '#047857'];
    div.style.background = 'white';
    div.style.padding = '8px 10px';
    div.style.borderRadius = '6px';
    div.style.boxShadow = '0 2px 6px rgba(0,0,0,0.15)';
    for (let i = 0; i < grades.length; i++) {
      const item = document.createElement('div');
      item.innerHTML = `<span style="display:inline-block;width:12px;height:12px;background:${colors[i]};margin-right:8px;border-radius:2px"></span>${grades[i]}`;
      div.appendChild(item);
    }
    return div;
  };
  legend.addTo(mapInstance);
}

async function initHoldingChart() {
  const regions = await fetchRegions();
  if (!regions.length) return;

  const values = regions
    .map(r => r.land_holding ?? r.average_land_holding)
    .filter(v => typeof v === 'number' && !isNaN(v))
    .sort((a,b) => a-b);
  const q = (p) => values.length ? values[Math.floor((values.length-1)*p)] : undefined;
  const q1 = q(0.25), q2 = q(0.5), q3 = q(0.75);

  const colorFor = (v) => {
    if (v == null) return '#9ca3af';
    if (q1 == null || q2 == null || q3 == null) return '#3b82f6';
    if (v <= q1) return '#a7f3d0';
    if (v <= q2) return '#34d399';
    if (v <= q3) return '#10b981';
    return '#047857';
  };

  const chartData = regions
    .filter(r => r.latitude && r.longitude)
    .map(r => ({
      name: r.name,
      value: r.land_holding ?? r.average_land_holding,
      color: colorFor(r.land_holding ?? r.average_land_holding)
    }))
    .sort((a, b) => (b.value || 0) - (a.value || 0))
    .slice(0, 15); // Show top 15 regions

  const ctx = document.getElementById('landHoldingChart').getContext('2d');
  
  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.map(d => d.name),
      datasets: [{
        label: 'Land Holding (ha)',
        data: chartData.map(d => d.value || 0),
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
              return `${context.parsed.y.toFixed(2)} ha`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Land Holding (hectares)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Regions'
          }
        }
      }
    }
  });
}

// Map toggle functionality
function toggleMap() {
  console.log('Toggle map clicked');
  const mapSection = document.getElementById('map-section');
  const chartSection = document.getElementById('chart-section');
  const toggleBtn = document.getElementById('toggle-map-btn');
  
  console.log('Map section:', mapSection);
  console.log('Toggle button:', toggleBtn);
  
  if (mapSection.style.display === 'none' || mapSection.style.display === '') {
    mapSection.style.display = 'block';
    chartSection.style.display = 'none';
    toggleBtn.textContent = '🗺️ Hide Map';
    toggleBtn.classList.add('active');
    document.getElementById('toggle-chart-btn').classList.remove('active');
    document.getElementById('toggle-chart-btn').textContent = '📊 Chart';
    console.log('Showing map');
    if (!mapInstance) {
      console.log('Initializing map');
      initHoldingMap();
    }
  } else {
    mapSection.style.display = 'none';
    toggleBtn.textContent = '🗺️ Map';
    toggleBtn.classList.remove('active');
    console.log('Hiding map');
  }
}

// Chart toggle functionality
function toggleChart() {
  console.log('Toggle chart clicked');
  const mapSection = document.getElementById('map-section');
  const chartSection = document.getElementById('chart-section');
  const toggleBtn = document.getElementById('toggle-chart-btn');
  
  if (chartSection.style.display === 'none' || chartSection.style.display === '') {
    chartSection.style.display = 'block';
    mapSection.style.display = 'none';
    toggleBtn.textContent = '📊 Hide Chart';
    toggleBtn.classList.add('active');
    document.getElementById('toggle-map-btn').classList.remove('active');
    document.getElementById('toggle-map-btn').textContent = '🗺️ Map';
    console.log('Showing chart');
    if (!chartInstance) {
      console.log('Initializing chart');
      initHoldingChart();
    }
  } else {
    chartSection.style.display = 'none';
    toggleBtn.textContent = '📊 Chart';
    toggleBtn.classList.remove('active');
    console.log('Hiding chart');
  }
}

// Update statistics with real data
async function updateStatistics() {
  const regions = await fetchRegions();
  if (!regions.length) return;

  // Calculate statistics
  const totalLandHolding = regions.reduce((sum, region) => {
    const landHolding = region.land_holding ?? region.average_land_holding;
    return sum + (landHolding || 0);
  }, 0);
  
  const avgLandHolding = totalLandHolding / regions.length;
  const avgYield = regions.reduce((sum, region) => sum + (region.yield_per_hectare || 0), 0) / regions.length;
  const avgRainfall = regions.reduce((sum, region) => sum + (region.rainfall || 0), 0) / regions.length;
  const statesCount = new Set(regions.map(region => region.state)).size;
  const irrigatedRegions = regions.filter(region => region.irrigation_area && region.irrigation_area > 0).length;
  const irrigationCoverage = (irrigatedRegions / regions.length * 100).toFixed(1);

  // Update summary statistics
  document.getElementById('total-land-holding').textContent = totalLandHolding.toLocaleString();
  document.getElementById('regions-count').textContent = regions.length;
  document.getElementById('avg-land-holding').textContent = avgLandHolding.toFixed(1);
  document.getElementById('states-count').textContent = statesCount;

  // Update KPI cards
  document.getElementById('kpi-regions-count').textContent = regions.length;
  document.getElementById('kpi-avg-land-holding').textContent = avgLandHolding.toFixed(1) + ' Ha';
  document.getElementById('kpi-avg-yield').textContent = avgYield.toFixed(1) + ' Q/Ha';
  document.getElementById('kpi-avg-rainfall').textContent = avgRainfall.toFixed(1) + ' mm';
  document.getElementById('kpi-irrigation-coverage').textContent = irrigationCoverage + '%';
  document.getElementById('kpi-states-count').textContent = statesCount;
}

// 🚪 Logout functionality
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, setting up event listeners');
  
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login/";
    });
  }
  
  const toggleMapBtn = document.getElementById('toggle-map-btn');
  const toggleChartBtn = document.getElementById('toggle-chart-btn');
  
  console.log('Map toggle button found:', toggleMapBtn);
  console.log('Chart toggle button found:', toggleChartBtn);
  
  if (toggleMapBtn) {
    toggleMapBtn.addEventListener('click', function(e) {
      console.log('Map button clicked!', e);
      toggleMap();
    });
    console.log('Map toggle event listener added');
  } else {
    console.error('Map toggle button not found!');
  }
  
  if (toggleChartBtn) {
    toggleChartBtn.addEventListener('click', function(e) {
      console.log('Chart button clicked!', e);
      toggleChart();
    });
    console.log('Chart toggle event listener added');
  } else {
    console.error('Chart toggle button not found!');
  }

  // Initialize table filtering
  initTableFiltering();
  
  // Initialize trend charts
  initTrendCharts();
  
  // Update statistics with real data
  updateStatistics();
});

// 🎥 Video debugging
document.addEventListener('DOMContentLoaded', function() {
  const video = document.querySelector('.dashboard-background-video');
  if (video) {
    console.log('Video element found:', video);
    
    video.addEventListener('loadstart', () => console.log('Video load started'));
    video.addEventListener('loadeddata', () => console.log('Video data loaded'));
    video.addEventListener('canplay', () => console.log('Video can play'));
    video.addEventListener('error', (e) => console.error('Video error:', e));
    
    // Try to play the video
    video.play().then(() => {
      console.log('Video playing successfully');
    }).catch((error) => {
      console.error('Video play failed:', error);
    });
  } else {
    console.error('Video element not found');
  }
});

// Table filtering functionality
function initTableFiltering() {
  const searchInput = document.getElementById('search-input');
  const soilFilter = document.getElementById('soil-filter');
  const table = document.querySelector('.land-table');
  const rows = table.querySelectorAll('tbody tr');

  function filterTable() {
    const searchTerm = searchInput.value.toLowerCase();
    const soilValue = soilFilter.value;

    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      const location = cells[1].textContent.toLowerCase();
      const crop = cells[4].textContent.toLowerCase();
      const soil = cells[3].textContent;

      const matchesSearch = searchTerm === '' || 
        location.includes(searchTerm) || 
        crop.includes(searchTerm) || 
        soil.toLowerCase().includes(searchTerm);

      const matchesSoil = soilValue === '' || soil === soilValue;

      if (matchesSearch && matchesSoil) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }

  if (searchInput) searchInput.addEventListener('input', filterTable);
  if (soilFilter) soilFilter.addEventListener('change', filterTable);
}

// Initialize trend charts
function initTrendCharts() {
  // Productivity Chart
  const productivityCtx = document.getElementById('productivityChart');
  if (productivityCtx) {
    new Chart(productivityCtx, {
      type: 'line',
      data: {
        labels: ['2020', '2021', '2022', '2023', '2024', '2025'],
        datasets: [{
          label: 'Productivity (Q/Acre)',
          data: [10.2, 11.8, 12.5, 13.1, 13.6, 14.2],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
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

  // Land Utilization Chart
  const utilizationCtx = document.getElementById('utilizationChart');
  if (utilizationCtx) {
    new Chart(utilizationCtx, {
      type: 'bar',
      data: {
        labels: ['2020', '2021', '2022', '2023', '2024', '2025'],
        datasets: [{
          label: 'Land Utilization (%)',
          data: [75, 78, 82, 85, 87, 85],
          backgroundColor: 'rgba(79, 195, 247, 0.8)',
          borderColor: '#4FC3F7',
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

// Enhanced map functionality with parcel boundaries
function enhanceMapWithParcels() {
  if (!mapInstance) return;

  // Add sample parcel boundaries (in real implementation, these would come from your data)
  const parcels = [
    {
      id: 'P-101',
      name: 'Village A',
      area: 25,
      soil: 'Loamy',
      crop: 'Wheat',
      productivity: 19,
      coordinates: [[28.6139, 77.2090], [28.6149, 77.2090], [28.6149, 77.2100], [28.6139, 77.2100]]
    },
    {
      id: 'P-102',
      name: 'Village B',
      area: 20,
      soil: 'Clay',
      crop: 'Fallow',
      productivity: 0,
      coordinates: [[28.6159, 77.2090], [28.6169, 77.2090], [28.6169, 77.2100], [28.6159, 77.2100]]
    }
  ];

  parcels.forEach(parcel => {
    const polygon = L.polygon(parcel.coordinates, {
      color: parcel.productivity > 15 ? '#4CAF50' : '#FF9800',
      weight: 2,
      fillColor: parcel.productivity > 15 ? '#4CAF50' : '#FF9800',
      fillOpacity: 0.3
    }).addTo(mapInstance);

    polygon.bindPopup(`
      <div style="min-width: 200px;">
        <h4>${parcel.id} - ${parcel.name}</h4>
        <p><strong>Area:</strong> ${parcel.area} acres</p>
        <p><strong>Soil:</strong> ${parcel.soil}</p>
        <p><strong>Crop:</strong> ${parcel.crop}</p>
        <p><strong>Productivity:</strong> ${parcel.productivity} Q/Acre</p>
      </div>
    `);
  });
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing land holding enhancements');
  
  // Initialize table filtering
  initTableFiltering();
  
  // Initialize trend charts
  initTrendCharts();
  
  // Enhanced map functionality will be called when map is toggled
  const originalToggleMap = toggleMap;
  toggleMap = function() {
    originalToggleMap();
    if (mapInstance) {
      setTimeout(enhanceMapWithParcels, 1000); // Delay to ensure map is fully loaded
    }
  };
});

// init on toggle only
