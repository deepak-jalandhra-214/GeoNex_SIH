from shapely.geometry import shape, mapping, Polygon
from shapely.strtree import STRtree
import numpy as np

class ChangeDetectionEngine:
    """
    AI-Based Incremental Change Detection Engine between two GIS survey datasets (T1 vs T2).
    Classifies changes into:
    - NEW: Added in T2 (Green)
    - REMOVED: Present in T1, missing in T2 (Red)
    - MODIFIED: Present in both, but footprint / area changed by > 15% (Yellow)
    - UNCHANGED: Remains identical
    """

    def __init__(self, iou_threshold=0.3, area_diff_threshold=0.15):
        self.iou_threshold = iou_threshold
        self.area_diff_threshold = area_diff_threshold

    def calculate_iou(self, poly1, poly2):
        """Calculates Intersection over Union (IoU) between two Shapely polygons."""
        try:
            if not poly1.intersects(poly2):
                return 0.0
            inter = poly1.intersection(poly2).area
            union = poly1.union(poly2).area
            if union == 0:
                return 0.0
            return inter / union
        except Exception:
            return 0.0

    def detect_changes(self, survey_t1_geojson, survey_t2_geojson):
        """
        Compares Baseline Survey T1 (e.g., 2025) with New Survey T2 (e.g., 2026).
        Returns GeoJSON FeatureCollection of change diffs with change_type properties.
        """
        t1_features = survey_t1_geojson.get("features", [])
        t2_features = survey_t2_geojson.get("features", [])

        t1_shapes = []
        for feat in t1_features:
            try:
                s = shape(feat["geometry"])
                if not s.is_valid:
                    s = s.buffer(0)
                t1_shapes.append((s, feat))
            except Exception:
                continue

        t2_shapes = []
        for feat in t2_features:
            try:
                s = shape(feat["geometry"])
                if not s.is_valid:
                    s = s.buffer(0)
                t2_shapes.append((s, feat))
            except Exception:
                continue

        matched_t1_indices = set()
        matched_t2_indices = set()

        change_features = []
        stats = {
            "new_count": 0,
            "removed_count": 0,
            "modified_count": 0,
            "unchanged_count": 0
        }

        # Compare each polygon in T2 against T1
        for idx2, (poly2, feat2) in enumerate(t2_shapes):
            best_iou = 0.0
            best_idx1 = -1

            for idx1, (poly1, feat1) in enumerate(t1_shapes):
                iou = self.calculate_iou(poly1, poly2)
                if iou > best_iou:
                    best_iou = iou
                    best_idx1 = idx1

            if best_iou >= self.iou_threshold:
                # Match found in T1
                matched_t1_indices.add(best_idx1)
                matched_t2_indices.add(idx2)

                poly1, feat1 = t1_shapes[best_idx1]
                area_diff = abs(poly2.area - poly1.area) / max(poly1.area, 1e-6)

                if area_diff > self.area_diff_threshold:
                    # MODIFIED feature
                    stats["modified_count"] += 1
                    mod_feat = {
                        "type": "Feature",
                        "id": f"change_mod_{idx2}",
                        "geometry": mapping(poly2),
                        "properties": {
                            "change_type": "MODIFIED",
                            "status_color": "#FFEA00", # Yellow
                            "class_name": feat2["properties"].get("class_name", "Building"),
                            "area_sq_m": feat2["properties"].get("area_sq_m", 0),
                            "area_change_pct": round(area_diff * 100, 1),
                            "description": f"Feature footprint altered by {round(area_diff*100, 1)}%"
                        }
                    }
                    change_features.append(mod_feat)
                else:
                    stats["unchanged_count"] += 1
            else:
                # No match in T1 -> NEW feature added in T2
                stats["new_count"] += 1
                new_feat = {
                    "type": "Feature",
                    "id": f"change_new_{idx2}",
                    "geometry": mapping(poly2),
                    "properties": {
                        "change_type": "NEW",
                        "status_color": "#00E676", # Green
                        "class_name": feat2["properties"].get("class_name", "Building"),
                        "area_sq_m": feat2["properties"].get("area_sq_m", 0),
                        "description": "New construction / feature detected"
                    }
                }
                change_features.append(new_feat)

        # Find features in T1 that were NOT matched in T2 -> REMOVED
        for idx1, (poly1, feat1) in enumerate(t1_shapes):
            if idx1 not in matched_t1_indices:
                stats["removed_count"] += 1
                rem_feat = {
                    "type": "Feature",
                    "id": f"change_rem_{idx1}",
                    "geometry": mapping(poly1),
                    "properties": {
                        "change_type": "REMOVED",
                        "status_color": "#FF1744", # Red
                        "class_name": feat1["properties"].get("class_name", "Building"),
                        "area_sq_m": feat1["properties"].get("area_sq_m", 0),
                        "description": "Demolished / removed structure"
                    }
                }
                change_features.append(rem_feat)

        change_geojson = {
            "type": "FeatureCollection",
            "features": change_features,
            "metadata": {
                "summary": stats,
                "total_changes": len(change_features),
                "survey_t1_date": "2025-05-10",
                "survey_t2_date": "2026-09-15"
            }
        }

        return change_geojson
