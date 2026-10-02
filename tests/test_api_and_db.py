import tempfile
import os
import json
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

from backend.database.geodb import GeoSpatialDatabaseManager
from backend.utils.sample_generator import generate_synthetic_drone_image
import backend.main as main_module
from backend.main import app

def test_geospatial_database_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = GeoSpatialDatabaseManager(db_dir=tmpdir)

        # Initial state check
        surveys = db.get_all_surveys()
        assert surveys == {}

        master = db.get_master_database()
        assert master["type"] == "FeatureCollection"
        assert master["features"] == []

        # Save survey
        sample_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "f1",
                    "geometry": {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]},
                    "properties": {"class_name": "Building"}
                }
            ]
        }
        db.save_survey("s1", sample_geojson, "Survey 1", "2026-01-01")

        s1 = db.get_survey("s1")
        assert s1 is not None
        assert s1["title"] == "Survey 1"
        assert len(s1["data"]["features"]) == 1

        # Update master with delta
        change_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "f1",
                    "geometry": {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]},
                    "properties": {"change_type": "NEW", "class_name": "Building"}
                }
            ]
        }
        updated_master = db.update_master_with_delta(sample_geojson, change_geojson)
        assert len(updated_master["features"]) == 1
        assert updated_master["features"][0]["id"] == "f1"

def test_sample_generator():
    with tempfile.TemporaryDirectory() as tmpdir:
        path_2025 = os.path.join(tmpdir, "2025.png")
        path_2026 = os.path.join(tmpdir, "2026.png")

        generate_synthetic_drone_image(path_2025, survey_year=2025, preset="classic")
        generate_synthetic_drone_image(path_2026, survey_year=2026, preset="presentation")

        assert os.path.exists(path_2025)
        assert os.path.exists(path_2026)

        img2025 = Image.open(path_2025)
        assert img2025.size == (600, 600)

def test_fastapi_endpoints():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override backend paths to isolate tests from production data/uploads
        orig_upload_dir = main_module.UPLOAD_DIR
        orig_data_dir = main_module.DATA_DIR
        orig_db_manager = main_module.db_manager

        test_upload_dir = os.path.join(tmpdir, "uploads")
        test_data_dir = os.path.join(tmpdir, "data_store")
        os.makedirs(test_upload_dir, exist_ok=True)
        os.makedirs(test_data_dir, exist_ok=True)

        main_module.UPLOAD_DIR = test_upload_dir
        main_module.DATA_DIR = test_data_dir
        main_module.db_manager = GeoSpatialDatabaseManager(db_dir=test_data_dir)

        try:
            client = TestClient(app)

            # Health endpoint
            r_health = client.get("/api/health")
            assert r_health.status_code == 200
            assert r_health.json()["status"] == "online"

            # Generate demo data endpoint
            r_demo = client.get("/api/generate-demo-data?style=classic")
            assert r_demo.status_code == 200
            demo_data = r_demo.json()
            assert demo_data["status"] == "success"
            assert "surveys" in demo_data

            # List surveys
            r_surveys = client.get("/api/surveys")
            assert r_surveys.status_code == 200
            surveys_list = r_surveys.json()
            assert len(surveys_list) >= 2

            # Get specific survey
            r_survey = client.get("/api/surveys/survey_2025")
            assert r_survey.status_code == 200
            assert r_survey.json()["survey_id"] == "survey_2025"

            # Change detection endpoint
            r_cd = client.post("/api/change-detection?t1_id=survey_2025&t2_id=survey_2026")
            assert r_cd.status_code == 200
            assert r_cd.json()["status"] == "success"

            # Master DB endpoint
            r_master = client.get("/api/master-db")
            assert r_master.status_code == 200
            assert r_master.json()["type"] == "FeatureCollection"

            # Upload and process endpoint
            with tempfile.NamedTemporaryFile(suffix=".png") as tmp_img:
                arr = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
                Image.fromarray(arr).save(tmp_img.name)
                tmp_img.seek(0)

                with open(tmp_img.name, "rb") as f:
                    response = client.post(
                        "/api/upload-and-process",
                        files={"file": ("upload.png", f, "image/png")},
                        data={
                            "survey_id": "test_upload_id",
                            "survey_title": "Test Upload",
                            "survey_date": "2026-10-01"
                        }
                    )
                assert response.status_code == 200
                assert response.json()["status"] == "success"
                assert response.json()["survey_id"] == "test_upload_id"
        finally:
            main_module.UPLOAD_DIR = orig_upload_dir
            main_module.DATA_DIR = orig_data_dir
            main_module.db_manager = orig_db_manager
