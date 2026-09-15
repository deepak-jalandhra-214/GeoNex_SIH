from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
import uuid
import json
from pathlib import Path

from backend.preprocessing.raster_processor import RasterProcessor
from backend.models.unet_plus_plus import GeospatialSegmentationPipeline
from backend.postprocessing.vectorizer import GISVectorizer
from backend.analysis.change_detection import ChangeDetectionEngine
from backend.database.geodb import GeoSpatialDatabaseManager
from backend.utils.sample_generator import generate_synthetic_drone_image

app = FastAPI(
    title="GeoNex - AI Drone Geospatial Mapping & Change Detection Engine",
    version="1.0.0",
    description="SIH 2026 Problem Statement 26012 Implementation"
)

# Enable CORS for frontend interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use absolute paths so the app does not depend on Vercel's working directory.
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
RUNTIME_DIR = Path("/tmp/geonex") if os.getenv("VERCEL") else BASE_DIR
UPLOAD_DIR = RUNTIME_DIR / "uploads"
DATA_DIR = RUNTIME_DIR / "data_store"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


# Initialize Core Services
raster_proc = RasterProcessor(tile_size=256, overlap=32)
ai_pipeline = GeospatialSegmentationPipeline()
vectorizer = GISVectorizer(min_polygon_area=12)
change_engine = ChangeDetectionEngine(iou_threshold=0.3, area_diff_threshold=0.15)
db_manager = GeoSpatialDatabaseManager(db_dir=str(DATA_DIR))


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "system": "GeoNex SIH 2026 AI Engine",
        "ai_model": "NumPy Spectral Segmentation",
        "device": str(ai_pipeline.device)
    }


@app.get("/api/generate-demo-data")
def generate_demo_data():
    """Generates baseline 2025 and new 2026 drone ortho-photos and runs automatic AI mapping."""
    img_2025_path = os.path.join(UPLOAD_DIR, "drone_survey_2025.png")
    img_2026_path = os.path.join(UPLOAD_DIR, "drone_survey_2026.png")

    generate_synthetic_drone_image(img_2025_path, survey_year=2025)
    generate_synthetic_drone_image(img_2026_path, survey_year=2026)

    # Process 2025 survey
    img_np_2025, shape_2025 = raster_proc.load_image(img_2025_path)
    mask_2025 = ai_pipeline.predict_mask(img_np_2025)
    geojson_2025 = vectorizer.raster_to_geojson(mask_2025)
    db_manager.save_survey("survey_2025", geojson_2025, "Baseline Survey 2025", "2025-05-10")

    # Process 2026 survey
    img_np_2026, shape_2026 = raster_proc.load_image(img_2026_path)
    mask_2026 = ai_pipeline.predict_mask(img_np_2026)
    geojson_2026 = vectorizer.raster_to_geojson(mask_2026)
    db_manager.save_survey("survey_2026", geojson_2026, "New Survey 2026", "2026-09-15")

    # Run change detection
    changes_geojson = change_engine.detect_changes(geojson_2025, geojson_2026)

    # Update Master Database with initial baseline
    db_manager.update_master_with_delta(geojson_2026, changes_geojson)

    return {
        "status": "success",
        "message": "Generated 2025 & 2026 drone surveys, AI segmentation, vectorization, and change detection!",
        "surveys": ["survey_2025", "survey_2026"],
        "changes_summary": changes_geojson.get("metadata", {}).get("summary", {})
    }


@app.post("/api/upload-and-process")
async def upload_and_process(
    file: UploadFile = File(...),
    survey_id: str = Form(...),
    survey_title: str = Form(...),
    survey_date: str = Form(...)
):
    """Uploads a drone aerial raster image (GeoTIFF/PNG/JPG) and processes AI vectorization."""
    file_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(file.filename)[1]
    saved_filename = f"drone_{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        img_np, shape = raster_proc.load_image(file_path)
        mask = ai_pipeline.predict_mask(img_np)
        geojson_res = vectorizer.raster_to_geojson(mask)

        db_manager.save_survey(survey_id, geojson_res, survey_title, survey_date)

        return {
            "status": "success",
            "survey_id": survey_id,
            "filename": saved_filename,
            "geojson": geojson_res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")


@app.get("/api/surveys")
def list_surveys():
    """Returns list of all registered surveys."""
    surveys = db_manager.get_all_surveys()
    summary_list = []
    for sid, sdata in surveys.items():
        summary_list.append({
            "survey_id": sid,
            "title": sdata.get("title"),
            "survey_date": sdata.get("survey_date"),
            "feature_count": sdata.get("data", {}).get("metadata", {}).get("total_features", 0)
        })
    return summary_list


@app.get("/api/surveys/{survey_id}")
def get_survey_data(survey_id: str):
    """Retrieves full GeoJSON for a given survey."""
    sdata = db_manager.get_survey(survey_id)
    if not sdata:
        raise HTTPException(status_code=404, detail="Survey not found")
    return sdata


@app.post("/api/change-detection")
def run_change_detection(t1_id: str = "survey_2025", t2_id: str = "survey_2026"):
    """Runs change detection between Survey T1 and Survey T2."""
    s1 = db_manager.get_survey(t1_id)
    s2 = db_manager.get_survey(t2_id)

    if not s1 or not s2:
        raise HTTPException(status_code=404, detail="One or both survey IDs not found")

    changes = change_engine.detect_changes(s1["data"], s2["data"])
    return {
        "status": "success",
        "t1_id": t1_id,
        "t2_id": t2_id,
        "changes": changes
    }


@app.post("/api/update-master-db")
def update_master_db(t2_id: str = "survey_2026", t1_id: str = "survey_2025"):
    """Applies incremental change updates to Master Geospatial Database."""
    s1 = db_manager.get_survey(t1_id)
    s2 = db_manager.get_survey(t2_id)

    if not s1 or not s2:
        raise HTTPException(status_code=404, detail="Surveys not found for database update")

    changes = change_engine.detect_changes(s1["data"], s2["data"])
    updated_master = db_manager.update_master_with_delta(s2["data"], changes)

    return {
        "status": "success",
        "message": "Master database updated incrementally based on AI change detection!",
        "master_metadata": updated_master.get("metadata", {})
    }


@app.get("/api/master-db")
def get_master_db():
    return db_manager.get_master_database()


# Mount static assets when they are present in the serverless bundle.
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
@app.get("/api")
@app.get("/api/")
@app.get("/api/index.py")
def read_root():
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(str(index_path))
    return JSONResponse({"status": "online", "message": "GeoNex API is running"})

