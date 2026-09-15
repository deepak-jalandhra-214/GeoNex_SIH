import json
import os
from datetime import datetime

class GeoSpatialDatabaseManager:
    """In-memory & JSON file persistent store for survey versions and master geospatial data."""

    def __init__(self, db_dir="data_store"):
        self.db_dir = db_dir
        os.makedirs(self.db_dir, exist_ok=True)
        self.surveys_file = os.path.join(self.db_dir, "surveys.json")
        self.master_file = os.path.join(self.db_dir, "master_geospatial.json")
        self._init_db()

    def _init_db(self):
        if not os.path.exists(self.surveys_file):
            with open(self.surveys_file, "w") as f:
                json.dump({}, f)

        if not os.path.exists(self.master_file):
            default_master = {
                "type": "FeatureCollection",
                "features": [],
                "metadata": {"last_updated": datetime.now().isoformat(), "version": 1}
            }
            with open(self.master_file, "w") as f:
                json.dump(default_master, f)

    def save_survey(self, survey_id, geojson_data, title, survey_date):
        """Saves a survey version into storage."""
        surveys = self.get_all_surveys()
        surveys[survey_id] = {
            "survey_id": survey_id,
            "title": title,
            "survey_date": survey_date,
            "created_at": datetime.now().isoformat(),
            "data": geojson_data
        }
        with open(self.surveys_file, "w") as f:
            json.dump(surveys, f, indent=2)

    def get_survey(self, survey_id):
        surveys = self.get_all_surveys()
        return surveys.get(survey_id)

    def get_all_surveys(self):
        try:
            with open(self.surveys_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_master_database(self):
        try:
            with open(self.master_file, "r") as f:
                return json.load(f)
        except Exception:
            return {"type": "FeatureCollection", "features": []}

    def update_master_with_delta(self, new_survey_geojson, change_geojson):
        """
        Updates the Master Database incrementally based on detected changes:
        - Inserts NEW features
        - Removes REMOVED features
        - Replaces MODIFIED features
        """
        master = self.get_master_database()
        master_features = {f.get("id"): f for f in master.get("features", [])}

        changes = change_geojson.get("features", [])
        for ch in changes:
            ch_type = ch["properties"].get("change_type")
            if ch_type == "NEW":
                feat_id = ch.get("id")
                master_features[feat_id] = ch
            elif ch_type == "REMOVED":
                feat_id = ch.get("id")
                master_features.pop(feat_id, None)
            elif ch_type == "MODIFIED":
                feat_id = ch.get("id")
                master_features[feat_id] = ch

        updated_master = {
            "type": "FeatureCollection",
            "features": list(master_features.values()),
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_features": len(master_features),
                "version": master.get("metadata", {}).get("version", 1) + 1
            }
        }

        with open(self.master_file, "w") as f:
            json.dump(updated_master, f, indent=2)

        return updated_master
