// Update with your ESP32's actual local IP address from the Serial Monitor
const ESP32_IP = "http://172.25.44.182"; 

// 1. Automatically fetch real TDS & Temperature from ESP32 every 2 seconds
async function fetchSensorData() {
  try {
    const response = await fetch(`${ESP32_IP}/api/data`);
    const data = await response.json();

    const tdsPpm = data.tds ? data.tds : 0;
    const tempC = data.temp ? data.temp : 0;

    document.getElementById('tds-value').textContent = tdsPpm.toFixed(1);
    document.getElementById('temperature-value').textContent = tempC.toFixed(1);
    
    // Get current pH value from the dashboard element
    const phElementText = document.getElementById('ph-value').textContent;
    const phVal = phElementText !== '--' ? parseFloat(phElementText) : null;

    // Categorize Water Status based on BOTH TDS and pH
    const statusEl = document.getElementById('water-status');

    // Check if sensor is dry / initializing
    if (tdsPpm === 0) {
        statusEl.textContent = "WATER STATUS: Initializing / Sensor Dry";
        statusEl.style.color = "#38bdf8";
        return;
    }

    // Evaluate pH warnings if pH has been generated
    let pHWarning = false;
    let pHTextStatus = "";
    if (phVal !== null) {
        if (phVal < 6.5) {
            pHWarning = true;
            pHTextStatus = " (Acidic pH)";
        } else if (phVal > 8.5) {
            pHWarning = true;
            pHTextStatus = " (Alkaline pH)";
        }
    }

    // Classification Logic combining TDS and pH
    if (tdsPpm > 900 || (phVal !== null && (phVal < 5.5 || phVal > 10.0))) {
        statusEl.textContent = "WATER STATUS: Poor / Unsafe (Extreme TDS or pH)";
        statusEl.style.color = "#f87171"; // Red
    } else if ((tdsPpm > 600 && tdsPpm <= 900) || pHWarning) {
        statusEl.textContent = `WATER STATUS: Fair / Marginal Quality${pHTextStatus}`;
        statusEl.style.color = "#fb923c"; // Orange
    } else if (tdsPpm > 300 && tdsPpm <= 600) {
        statusEl.textContent = "WATER STATUS: Good / Acceptable";
        statusEl.style.color = "#facc15"; // Yellow
    } else if (tdsPpm >= 50 && tdsPpm <= 300) {
        statusEl.textContent = "WATER STATUS: Excellent / Optimal Drinking Water";
        statusEl.style.color = "#4ade80"; // Green
    } else {
        statusEl.textContent = "WATER STATUS: Checking Parameters...";
        statusEl.style.color = "#38bdf8";
    }

  } catch (error) {
    console.error("Error fetching data from ESP32:", error);
    document.getElementById('water-status').textContent = "WATER STATUS: Waiting for ESP32 connection...";
  }
}

// 2. Button click listener for generating the random pH value
const button = document.getElementById('generate-ph');
const display = document.getElementById('ph-value');

if (button && display) {
    button.addEventListener('click', () => {
        const phValue = Number((Math.random() * (13 - 0) + 1).toFixed(2));
        display.textContent = phValue;
        // Immediately re-run check so status updates when pH changes
        fetchSensorData();
    });
}

// Start background polling for ESP32 sensor
setInterval(fetchSensorData, 2000);
fetchSensorData();