import tempfile
import os
import numpy as np
from PIL import Image

from backend.preprocessing.raster_processor import RasterProcessor
from backend.models.unet_plus_plus import GeospatialSegmentationPipeline
from backend.postprocessing.vectorizer import GISVectorizer
from backend.analysis.change_detection import ChangeDetectionEngine

def test_raster_processor():
    processor = RasterProcessor(tile_size=256, overlap=32)
    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = os.path.join(tmpdir, "test.png")
        arr = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
        Image.fromarray(arr).save(img_path)

        img_np, shape = processor.load_image(img_path)
        assert shape == (300, 300)
        assert img_np.shape == (300, 300, 3)
        assert img_np.dtype == np.float32

        tiles = processor.create_tiles(img_np)
        assert len(tiles) > 0
        for item in tiles:
            tile = item['tile']
            assert tile.shape[0] == 256 and tile.shape[1] == 256

def test_segmentation_pipeline():
    pipeline = GeospatialSegmentationPipeline()
    img_np = np.zeros((100, 100, 3), dtype=np.float32)
    # Add water color normalized to [0, 1] (b=220, g=100, r=20)
    img_np[10:30, 10:30] = [20.0 / 255.0, 100.0 / 255.0, 220.0 / 255.0]

    mask = pipeline.predict_mask(img_np)
    assert mask.shape == (100, 100)
    assert np.all((mask >= 0) & (mask <= 4))
    # Water pixel at (15, 15) should be classified as water class 3
    assert mask[15, 15] == 3

def test_gis_vectorizer():
    vectorizer = GISVectorizer(min_polygon_area=12)
    mask = np.zeros((100, 100), dtype=np.uint8)
    # Create a building rectangle (class 1)
    mask[20:60, 20:60] = 1

    geojson = vectorizer.raster_to_geojson(mask)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) > 0

    feat = geojson["features"][0]
    assert feat["type"] == "Feature"
    assert feat["properties"]["class_id"] == 1
    assert feat["properties"]["class_name"] == "Building"
    assert feat["geometry"]["type"] in ["Polygon", "MultiPolygon"]

def test_change_detection_engine():
    engine = ChangeDetectionEngine(iou_threshold=0.3, area_diff_threshold=0.15)

    # T1 GeoJSON with 1 building
    t1_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "feat_1",
                "properties": {"class_id": 1, "class_name": "Building", "area_m2": 100},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[77.21, 28.62], [77.22, 28.62], [77.22, 28.61], [77.21, 28.61], [77.21, 28.62]]]
                }
            }
        ]
    }

    # T2 GeoJSON with same building + 1 new building
    t2_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "feat_1",
                "properties": {"class_id": 1, "class_name": "Building", "area_m2": 100},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[77.21, 28.62], [77.22, 28.62], [77.22, 28.61], [77.21, 28.61], [77.21, 28.62]]]
                }
            },
            {
                "type": "Feature",
                "id": "feat_2",
                "properties": {"class_id": 1, "class_name": "Building", "area_m2": 80},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[77.23, 28.64], [77.24, 28.64], [77.24, 28.63], [77.23, 28.63], [77.23, 28.64]]]
                }
            }
        ]
    }

    result = engine.detect_changes(t1_geojson, t2_geojson)
    assert result["type"] == "FeatureCollection"
    # Unchanged features are not in changes output, only 1 new change feature
    features = result["features"]
    assert len(features) == 1
    assert features[0]["properties"]["change_type"] == "NEW"
    assert result["metadata"]["summary"]["unchanged_count"] == 1
    assert result["metadata"]["summary"]["new_count"] == 1
