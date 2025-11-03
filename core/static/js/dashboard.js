// dashboard.js

const BASE_URL = "http://127.0.0.1:8000/api/regions/";
const SUMMARY_URL = "http://127.0.0.1:8000/api/regions/summary/";

function buildQuery(params){
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([k,v]) => { if (v) usp.set(k, v); });
  const qs = usp.toString();
  return qs ? `?${qs}` : "";
}

// 🌾 Fetch region data (handles token refresh automatically)
async function fetchRegionData(retry = true) {
  try {
    const url = BASE_URL + buildQuery(currentFilters);
    const res = await fetch(url, { headers: { "Content-Type": "application/json" } });

    if (!res.ok) {
      console.error("Error fetching region data:", res.status);
      return [];
    }

    return await res.json();
  } catch (err) {
    console.error("Fetch error:", err);
    return [];
  }
}

async function fetchSummary() {
  try {
    const url = SUMMARY_URL + buildQuery(currentFilters);
    const res = await fetch(url, { headers: { "Content-Type": "application/json" } });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('Summary fetch failed', e);
    return null;
  }
}

// Legacy card rendering removed - now using static agriculture insights

// Chart functionality removed per request

// 🗺️ Render Leaflet map with region markers
// Map removed from dashboard per request

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
});

// 🚀 Initialize dashboard with hover interactions
document.addEventListener('DOMContentLoaded', function() {
  const insightTitles = document.querySelectorAll('.insight-title');
  const detailBoxes = document.querySelectorAll('.detail-box');
  
  insightTitles.forEach(title => {
    const detailsId = title.getAttribute('data-details');
    const detailBox = document.getElementById(detailsId);
    
    title.addEventListener('mouseenter', () => {
      console.log('Mouse entered:', detailsId); // Debug log
      
      // Hide all other detail boxes
      detailBoxes.forEach(box => {
        box.classList.remove('show');
      });
      
      // Show current detail box
      if (detailBox) {
        detailBox.classList.add('show');
        console.log('Showing detail box:', detailsId); // Debug log
      }
    });
    
    title.addEventListener('mouseleave', () => {
      // Hide detail box after a short delay
      setTimeout(() => {
        if (detailBox) {
          detailBox.classList.remove('show');
          console.log('Hiding detail box:', detailsId); // Debug log
        }
      }, 100);
    });
  });
  
  console.log('Dashboard hover interactions initialized'); // Debug log
});

// Filters wiring
// Filters removed from dashboard per request
