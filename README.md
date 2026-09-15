# GeoNex - AI Drone Geospatial Mapping & Change Detection Engine

> **Smart India Hackathon 2026** • **Problem Statement ID: 26012**  
> *Autonomous drone aerial imagery vectorization, multi-class feature extraction, incremental change detection, and cadastral database updating.*

---

## 🌟 Overview

**GeoNex** is an AI-powered Web GIS platform designed to convert high-resolution aerial drone orthophotos (GeoTIFF / PNG / JPG) into map-ready vector layers (Buildings, Roads, Water Bodies, Rooftops). 

By comparing successive drone surveys (e.g., 2025 Baseline vs 2026 Current), GeoNex automatically detects urban changes (New constructions, Demolitions, Footprint modifications) and incrementally updates a central Master Geospatial Database without costly manual digitization.

---

## ✨ Key Features

- **🛸 Drone Imagery Upload & Preprocessing**: Drag-and-drop aerial raster loader with automatic image tiling, normalization, and geo-referencing.
- **🧠 Lightweight AI Segmentation Pipeline**: Multi-class spectral & neural feature segmentation for urban feature extraction.
- **📐 Raster-to-GeoJSON Vectorization**: Morphological noise filtering and polygonization into standard OGC GeoJSON vector layers.
- **🔄 Incremental Change Detection Engine**: Polygon IoU comparison engine identifying:
  - 🟢 **NEW**: Added in current survey (Green)
  - 🔴 **REMOVED**: Demolished structures (Red)
  - 🟡 **MODIFIED**: Footprint modified by >15% (Yellow)
- **🗄️ Master Geospatial Database Sync**: Delta update sync updating only changed parcels in the master database.
- **🎨 Glassmorphic Interactive GIS Dashboard**: Built with high-contrast carto maps, floating counter pills, live layer toggles, and modal architecture diagrams.
- **☁️ Zero-Config Vercel Deployment**: Configured with `@vercel/python` serverless entrypoint and edge static delivery.

---

## 🏗️ System Architecture

```text
  [ 🛸 Drone Imagery ] ➔ [ ⚙️ Preprocessor (Tiling) ] ➔ [ 🧠 AI Model (UNet++) ]
                                                                 │
  [ 🗄️ Master Map Sync ] ⇦ [ 🔄 Change Engine ] ⇦ [ 📐 Vectorizer (GeoJSON) ]
```

---

## 📁 Repository Structure

```text
.
├── api/
│   └── index.py               # Vercel Serverless Function entrypoint
├── backend/
│   ├── analysis/              # Change detection engine (IoU polygon matching)
│   ├── database/              # Survey & master-map persistence (GeoSpatial Database)
│   ├── models/                # Lightweight NumPy segmentation pipeline
│   ├── postprocessing/        # Raster-to-GeoJSON vectorizer
│   ├── preprocessing/         # Image loader and overlapping tiling
│   ├── utils/                 # Synthetic aerial image generator
│   └── main.py                # FastAPI backend application & API routes
├── data_store/                # Saved survey JSON & master geospatial database
├── static/
│   ├── css/
│   │   └── styles.css         # Glassmorphism aesthetic system & responsive styles
│   ├── js/
│   │   └── app.js             # Leaflet map logic, API interactions & dropzone
│   ├── index.html             # Main GIS Dashboard interface
│   └── slides.html            # SIH 2026 Presentation Deck
├── pyproject.toml             # Project metadata & headless Python dependencies
├── requirements.txt           # Vercel / serverless runtime dependencies
├── vercel.json                # Vercel deployment routing & rewrites
└── run.py                     # Local server launcher script
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- **Python 3.10+**
- **pip**

### 1. Clone & Setup Virtual Environment

```powershell
# Activate Virtual Environment (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run the Server

```powershell
python run.py
```

### 3. Open Dashboard

- **Web Dashboard**: [`http://127.0.0.1:8000`](http://127.0.0.1:8000)
- **API Swagger Documentation**: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- **Interactive Presentation Deck**: [`http://127.0.0.1:8000/slides`](http://127.0.0.1:8000/slides)

---

## 🌐 Deploying to Vercel

The application is pre-configured for Vercel Serverless Functions using `api/index.py` and `opencv-python-headless`.

### One-Click Git Deployment
1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Deploy GeoNex to Vercel"
   git push origin main
   ```
2. Connect your repository in Vercel Dashboard.
3. Vercel automatically detects `api/index.py` and deploys the FastAPI backend + static CDN frontend!

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status & model device check |
| `GET` | `/api/generate-demo-data` | Generates 2025 & 2026 drone surveys & runs full pipeline |
| `POST` | `/api/upload-and-process` | Upload aerial raster image & receive vector GeoJSON |
| `GET` | `/api/surveys` | List all registered survey versions |
| `GET` | `/api/surveys/{survey_id}` | Fetch full GeoJSON for a specific survey |
| `POST` | `/api/change-detection` | Compare baseline vs current survey for polygon diffs |
| `POST` | `/api/update-master-db` | Apply detected changes to Master Geospatial Database |
| `GET` | `/api/master-db` | Fetch current Master Geospatial Database GeoJSON |

---

## 🏆 Smart India Hackathon 2026 Details

- **Problem Statement**: PS 26012 (Smart Automation for Urban Cadastral Mapping)
- **Domain**: AI / GIS / Remote Sensing
- **Theme**: Smart Automation & AI Geo-Intelligence

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
