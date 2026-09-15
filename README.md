# GeoNex

AI-powered drone geospatial mapping and change detection for Smart India Hackathon 2026, Problem Statement 26012.

GeoNex converts aerial imagery into map-ready geospatial features such as buildings, roads, water bodies, and rooftops. It compares successive surveys, identifies changed areas, and updates a master geospatial database incrementally.

## Highlights

- Drone imagery upload through a web dashboard
- Multi-feature segmentation pipeline
- Raster-to-GeoJSON vectorization
- Baseline and new-survey comparison
- Incremental master geospatial database updates
- Interactive map layers and survey selection
- Synthetic 2025 and 2026 demo datasets for quick evaluation
- FastAPI backend with a browser-based frontend

## Workflow

```text
Drone imagery
    -> Raster preprocessing
    -> AI segmentation
    -> Building / road / water / rooftop features
    -> GeoJSON vectorization
    -> Survey database
    -> Change detection
    -> Incremental master-map update
```

## Project Structure

```text
.
├── backend/
│   ├── analysis/          # Change detection
│   ├── database/          # Survey and master-map persistence
│   ├── models/            # Geospatial segmentation model
│   ├── postprocessing/    # Raster-to-vector conversion
│   ├── preprocessing/     # Image loading and tiling
│   └── main.py            # FastAPI application and API routes
├── data_store/            # JSON survey and master-map data
├── static/
│   ├── index.html         # Web dashboard
│   ├── css/               # Dashboard styles
│   └── js/                # Dashboard behavior
├── uploads/               # Uploaded and generated imagery
├── run.py                 # Local server entry point
├── requirements.txt       # Python dependencies
└── generate_ppt.py        # Presentation-generation utility
```

## Requirements

- Python 3.10 or newer recommended
- pip
- Optional GPU with a compatible PyTorch installation for faster inference

## Installation

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows, if PowerShell blocks activation for the current session, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

## Run the Application

```powershell
python run.py
```

Open the dashboard at:

```text
http://127.0.0.1:8000
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The server uses reload mode during development. Stop it with `Ctrl+C`.

## Quick Demo

1. Start the server.
2. Open the dashboard.
3. Select **Load SIH 2026 Datasets**.
4. The application generates baseline and new synthetic surveys.
5. It runs segmentation, vectorization, change detection, and a master-map update.
6. Use the active survey selector to inspect the available layers.

The demo endpoint can also be called directly:

```text
GET http://127.0.0.1:8000/api/generate-demo-data
```

## API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check service and model status |
| `GET` | `/api/generate-demo-data` | Generate and process demo surveys |
| `POST` | `/api/upload-and-process` | Upload and process an image |
| `GET` | `/api/surveys` | List stored surveys |
| `GET` | `/api/surveys/{survey_id}` | Retrieve one survey's GeoJSON |
| `POST` | `/api/change-detection` | Compare two stored surveys |
| `POST` | `/api/update-master-db` | Apply detected changes to the master map |
| `GET` | `/api/master-db` | Retrieve the master geospatial database |

Interactive request and response schemas are available in FastAPI Swagger at `/docs`.

### Upload example

The upload endpoint expects multipart form data:

- `file`: PNG, JPG, or GeoTIFF image
- `survey_id`: unique survey identifier
- `survey_title`: human-readable survey name
- `survey_date`: survey date, for example `2026-09-15`

Example with PowerShell:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/upload-and-process `
  -F "file=@uploads/drone_survey_2026.png" `
  -F "survey_id=survey_custom" `
  -F "survey_title=Custom Survey" `
  -F "survey_date=2026-09-15"
```

## Data and Storage

The current prototype stores survey and master-map data as JSON files in `data_store/`. Uploaded and generated images are stored in `uploads/`.

For a production deployment, replace or extend this storage layer with a managed spatial database such as PostgreSQL with PostGIS and add object storage for large raster files.

## Current Prototype Scope

This repository is a working demonstration of the GeoNex workflow. It is designed for local evaluation and hackathon prototyping. Production use would require validated training data, model evaluation metrics, geospatial coordinate handling for each input format, authentication, access control, durable spatial storage, and deployment monitoring.

Do not interpret generated demo results as measured model performance. Add benchmark results only after testing against a documented labelled dataset.

## Presentation

The project presentation is available in the repository as `presentation.html`. The presentation improvement workflow is documented in [`.github/skills/improve-presentation-deck/SKILL.md`](.github/skills/improve-presentation-deck/SKILL.md).

## Team

**GeoNex**

- Smart India Hackathon 2026
- Problem Statement ID: 26012
- Theme: Smart Automation
- Category: Software

## License

No license has been specified yet. Add a license before accepting external contributions or distributing the project publicly.
