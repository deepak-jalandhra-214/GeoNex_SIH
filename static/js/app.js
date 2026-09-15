// GeoNex SIH 2026 - Interactive Web GIS Application Logic

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Leaflet Map
    const initialCoords = [28.6195, 77.2170]; // Delhi/India Geospatial Center
    const map = L.map("map", {
        center: initialCoords,
        zoom: 16,
        zoomControl: false
    });

    // Add Zoom Control to top-left
    L.control.zoom({ position: 'topleft' }).addTo(map);

    // Dark Satellite / Vector Tile Layer
    const baseTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 20,
        subdomains: 'abcd',
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO & GeoNex SIH 2026'
    }).addTo(map);

    // State Variables
    let geojsonLayerGroup = L.layerGroup().addTo(map);
    let currentGeoJSON = null;
    let currentViewMode = "survey_2026";
    let activeCategoryFilters = {
        1: true, // Buildings
        2: true, // Roads
        3: true, // Water
        4: true  // Rooftops
    };

    // DOM Elements
    const btnLoadDemo = document.getElementById("btn-load-demo");
    const selectSurveyView = document.getElementById("select-survey-view");
    const uploadForm = document.getElementById("upload-form");
    const btnUpdateMaster = document.getElementById("btn-update-master");
    const btnViewChanges = document.getElementById("btn-view-changes");
    const mapViewTitle = document.getElementById("map-view-title");
    const mapViewSubtitle = document.getElementById("map-view-subtitle");
    
    const statTotalFeatures = document.getElementById("stat-total-features");
    const statChangedCount = document.getElementById("stat-changed-count");
    const statMasterVer = document.getElementById("stat-master-ver");
    const aiStatusText = document.getElementById("ai-status-text");

    // Category Color Mapping
    function getFeatureStyle(feature) {
        const props = feature.properties || {};

        // Change Detection Overlay Styling
        if (props.change_type) {
            let color = "#00E676"; // Default NEW (Green)
            if (props.change_type === "REMOVED") color = "#FF1744"; // Red
            if (props.change_type === "MODIFIED") color = "#FFEA00"; // Yellow

            return {
                color: color,
                weight: 3,
                opacity: 0.95,
                fillColor: color,
                fillOpacity: 0.45
            };
        }

        // Standard Multi-Feature Styling
        const color = props.color || "#00E676";
        return {
            color: color,
            weight: 2,
            opacity: 0.9,
            fillColor: color,
            fillOpacity: 0.35
        };
    }

    // Render GeoJSON Features onto Leaflet Map
    function renderGeoJSON(geojsonData) {
        geojsonLayerGroup.clearLayers();
        currentGeoJSON = geojsonData;

        if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) {
            statTotalFeatures.textContent = "0";
            return;
        }

        let totalRendered = 0;
        let bounds = L.latLngBounds();

        const geoLayer = L.geoJSON(geojsonData, {
            filter: function(feature) {
                // Filter by category toggles if standard feature
                const classId = feature.properties?.class_id;
                if (classId && activeCategoryFilters[classId] === false) {
                    return false;
                }
                return true;
            },
            style: getFeatureStyle,
            onEachFeature: function(feature, layer) {
                totalRendered++;
                const p = feature.properties || {};
                
                // Build popup content
                let popupHtml = `
                    <div style="font-family: sans-serif; padding: 4px;">
                        <h4 style="margin: 0 0 6px 0; color: ${p.color || p.status_color || '#00E676'}">
                            ${p.change_type ? 'Change: ' + p.change_type : (p.class_name || 'Geo Feature')}
                        </h4>
                        <div style="font-size: 12px; color: #333;">
                            <b>ID:</b> ${p.id || 'N/A'}<br/>
                            ${p.area_sq_m ? `<b>Area:</b> ${p.area_sq_m} sq. m<br/>` : ''}
                            ${p.confidence ? `<b>Confidence:</b> ${(p.confidence * 100).toFixed(1)}%<br/>` : ''}
                            ${p.description ? `<b>Note:</b> ${p.description}<br/>` : ''}
                        </div>
                    </div>
                `;
                layer.bindPopup(popupHtml);

                // Add mouseover highlight
                layer.on({
                    mouseover: function(e) {
                        const l = e.target;
                        l.setStyle({ fillOpacity: 0.7, weight: 4 });
                    },
                    mouseout: function(e) {
                        geoLayer.resetStyle(e.target);
                    }
                });

                // Extend map bounds
                if (layer.getBounds) {
                    bounds.extend(layer.getBounds());
                }
            }
        });

        geoLayer.addTo(geojsonLayerGroup);
        statTotalFeatures.textContent = totalRendered;

        // Auto-fit map viewport to dataset features
        if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [40, 40] });
        }
    }

    // API Call: Fetch Data by Active View
    async function loadActiveView(viewMode) {
        currentViewMode = viewMode;
        aiStatusText.textContent = `Fetching ${viewMode}...`;

        const viewCopy = {
            survey_2025: ["Baseline Survey", "2025", "Original mapped features for comparison"],
            survey_2026: ["New Survey", "2026", "AI-extracted geospatial features ready for review"],
            changes: ["Detected Changes", "2025 → 2026", "Only changed areas are highlighted"],
            master: ["Master Geospatial Map", "LIVE", "Incremental map updated from approved surveys"]
        };
        const copy = viewCopy[viewMode];
        if (copy && mapViewTitle && mapViewSubtitle) {
            mapViewTitle.innerHTML = `${copy[0]} <em>${copy[1]}</em>`;
            mapViewSubtitle.textContent = copy[2];
        }

        try {
            if (viewMode === "changes") {
                const res = await fetch("/api/change-detection?t1_id=survey_2025&t2_id=survey_2026", { method: "POST" });
                const json = await res.json();
                renderGeoJSON(json.changes);
                
                const stats = json.changes.metadata?.summary || {};
                statChangedCount.textContent = json.changes.metadata?.total_changes || 0;
                aiStatusText.textContent = `AI Change Detection Complete (New: ${stats.new_count || 0}, Mod: ${stats.modified_count || 0})`;
            } else if (viewMode === "master") {
                const res = await fetch("/api/master-db");
                const masterData = await res.json();
                renderGeoJSON(masterData);
                statMasterVer.textContent = `v${masterData.metadata?.version || 1}`;
                aiStatusText.textContent = "Master Geospatial DB Active";
            } else {
                const res = await fetch(`/api/surveys/${viewMode}`);
                if (!res.ok) {
                    // Trigger demo generation first if survey missing
                    await fetch("/api/generate-demo-data");
                    const resRetry = await fetch(`/api/surveys/${viewMode}`);
                    const surveyObj = await resRetry.json();
                    renderGeoJSON(surveyObj.data);
                } else {
                    const surveyObj = await res.json();
                    renderGeoJSON(surveyObj.data);
                }
                aiStatusText.textContent = `Showing ${viewMode}`;
            }
        } catch (err) {
            console.error("Error loading view:", err);
            aiStatusText.textContent = "Ready";
        }
    }

    // Event Listener: Demo Quick Start Button
    btnLoadDemo.addEventListener("click", async () => {
        aiStatusText.textContent = "Generating SIH 2026 Datasets...";
        btnLoadDemo.disabled = true;

        try {
            const res = await fetch("/api/generate-demo-data");
            const data = await res.json();
            
            // Set view to 2026 survey
            selectSurveyView.value = "survey_2026";
            await loadActiveView("survey_2026");

            // Update change count
            const changeRes = await fetch("/api/change-detection?t1_id=survey_2025&t2_id=survey_2026", { method: "POST" });
            const changeJson = await changeRes.json();
            statChangedCount.textContent = changeJson.changes.metadata?.total_changes || 0;

            aiStatusText.textContent = "SIH 2026 Demo Loaded Successfully!";
        } catch (err) {
            alert("Failed to load demo data: " + err.message);
            aiStatusText.textContent = "Error loading demo";
        } finally {
            btnLoadDemo.disabled = false;
        }
    });

    // Event Listener: View Selection Dropdown
    selectSurveyView.addEventListener("change", (e) => {
        loadActiveView(e.target.value);
    });

    if (btnViewChanges) {
        btnViewChanges.addEventListener("click", () => {
            selectSurveyView.value = "changes";
            loadActiveView("changes");
        });
    }

    // Event Listener: Upload Drone Raster Form
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById("input-file");
        const surveyIdInput = document.getElementById("input-survey-id");

        if (!fileInput.files || fileInput.files.length === 0) return;

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("survey_id", surveyIdInput.value.trim() || "survey_custom");
        formData.append("survey_title", "Custom Drone Survey");
        formData.append("survey_date", new Date().toISOString().split("T")[0]);

        aiStatusText.textContent = "Processing UNet++ Segmentation & Polygonization...";

        try {
            const res = await fetch("/api/upload-and-process", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            
            // Add new option to dropdown
            const opt = document.createElement("option");
            opt.value = data.survey_id;
            opt.textContent = `Custom (${data.survey_id})`;
            selectSurveyView.appendChild(opt);
            selectSurveyView.value = data.survey_id;

            renderGeoJSON(data.geojson);
            aiStatusText.textContent = "Extraction Complete!";
        } catch (err) {
            alert("Upload failed: " + err.message);
            aiStatusText.textContent = "Upload Error";
        }
    });

    // Event Listener: Master Database Sync Button
    btnUpdateMaster.addEventListener("click", async () => {
        aiStatusText.textContent = "Applying Incremental Update to Master DB...";
        try {
            const res = await fetch("/api/update-master-db", { method: "POST" });
            const data = await res.json();
            
            selectSurveyView.value = "master";
            await loadActiveView("master");

            aiStatusText.textContent = "Master Database Updated!";
        } catch (err) {
            alert("Failed to update master DB: " + err.message);
        }
    });

    // Event Listeners: Layer Filter Toggles
    document.getElementById("toggle-buildings").addEventListener("change", (e) => {
        activeCategoryFilters[1] = e.target.checked;
        if (currentGeoJSON) renderGeoJSON(currentGeoJSON);
    });
    document.getElementById("toggle-roads").addEventListener("change", (e) => {
        activeCategoryFilters[2] = e.target.checked;
        if (currentGeoJSON) renderGeoJSON(currentGeoJSON);
    });
    document.getElementById("toggle-water").addEventListener("change", (e) => {
        activeCategoryFilters[3] = e.target.checked;
        if (currentGeoJSON) renderGeoJSON(currentGeoJSON);
    });
    document.getElementById("toggle-rooftops").addEventListener("change", (e) => {
        activeCategoryFilters[4] = e.target.checked;
        if (currentGeoJSON) renderGeoJSON(currentGeoJSON);
    });

    // Event Listeners: System Architecture Modal
    const archModal = document.getElementById("arch-modal");
    const btnViewArch = document.getElementById("btn-view-architecture");
    const btnCloseArch = document.getElementById("btn-close-arch-modal");

    if (btnViewArch && archModal) {
        btnViewArch.addEventListener("click", () => {
            archModal.style.display = "flex";
        });
    }

    if (btnCloseArch && archModal) {
        btnCloseArch.addEventListener("click", () => {
            archModal.style.display = "none";
        });
    }

    if (archModal) {
        archModal.addEventListener("click", (e) => {
            if (e.target === archModal) {
                archModal.style.display = "none";
            }
        });
    }

    // Initial Load: Auto-trigger demo initialization
    loadActiveView("survey_2026");
});
