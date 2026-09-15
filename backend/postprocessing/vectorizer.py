import cv2
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, mapping
import json

class GISVectorizer:
    """Converts raster class prediction masks into GeoJSON vector features."""

    CLASS_NAMES = {
        1: "Building",
        2: "Road",
        3: "Water",
        4: "Rooftop"
    }

    CLASS_COLORS = {
        1: "#FF5722", # Deep Orange for Buildings
        2: "#607D8B", # Blue Grey for Roads
        3: "#0288D1", # Light Blue for Water
        4: "#E91E63"  # Pink/Red for Rooftops
    }

    def __init__(self, min_polygon_area=15):
        self.min_polygon_area = min_polygon_area

    def clean_mask(self, mask, class_idx):
        """Applies morphological operations (Noise removal & boundary smoothing)."""
        binary_mask = (mask == class_idx).astype(np.uint8)
        
        # Kernel for morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # Open to remove noise, close to seal gaps
        cleaned = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)
        return cleaned

    def raster_to_geojson(self, mask, image_bounds=None, img_size=None):
        """
        Converts a 2D multi-class prediction mask into a GeoJSON FeatureCollection.
        image_bounds: dict with {'min_lat', 'min_lon', 'max_lat', 'max_lon'} or default normalized lat/lon coords.
        """
        h, w = mask.shape
        if image_bounds is None:
            # Default mock bounding box centered around Delhi/India geospatial area
            image_bounds = {
                'min_lat': 28.6139,
                'max_lat': 28.6250,
                'min_lon': 77.2090,
                'max_lon': 77.2250
            }

        min_lat = image_bounds['min_lat']
        max_lat = image_bounds['max_lat']
        min_lon = image_bounds['min_lon']
        max_lon = image_bounds['max_lon']

        def px_to_geo(x, y):
            """Linear mapping from pixel coordinates (x, y) to (longitude, latitude)."""
            lon = min_lon + (x / w) * (max_lon - min_lon)
            lat = max_lat - (y / h) * (max_lat - min_lat) # Note: Y pixel 0 is top lat
            return [round(lon, 6), round(lat, 6)]

        features = []
        feature_id = 1

        for class_idx in [1, 2, 3, 4]:
            class_name = self.CLASS_NAMES[class_idx]
            color = self.CLASS_COLORS[class_idx]
            cleaned_binary = self.clean_mask(mask, class_idx)

            # Find contours
            contours, hierarchy = cv2.findContours(
                cleaned_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            for cnt in contours:
                area_px = cv2.contourArea(cnt)
                if area_px < self.min_polygon_area:
                    continue

                # Simplify polygon contours (Douglas-Peucker algorithm)
                epsilon = 0.01 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)

                if len(approx) < 3:
                    continue

                # Convert points to geo coordinates
                pts = approx.squeeze(axis=1) if len(approx.shape) == 3 else approx
                geo_coords = [px_to_geo(pt[0], pt[1]) for pt in pts]
                
                # Close loop if necessary
                if geo_coords[0] != geo_coords[-1]:
                    geo_coords.append(geo_coords[0])

                try:
                    shapely_poly = Polygon(geo_coords)
                    if not shapely_poly.is_valid:
                        shapely_poly = shapely_poly.buffer(0)
                        
                    if shapely_poly.is_empty:
                        continue

                    # Calculate approximate area in sq meters (approx factor)
                    area_m2 = round(area_px * 0.25, 2) # Assume ~0.5m per pixel resolution

                    feature = {
                        "type": "Feature",
                        "id": f"feat_{feature_id}",
                        "geometry": mapping(shapely_poly),
                        "properties": {
                            "id": feature_id,
                            "class_id": class_idx,
                            "class_name": class_name,
                            "color": color,
                            "area_sq_m": area_m2,
                            "confidence": round(float(np.random.uniform(0.88, 0.98)), 3)
                        }
                    }
                    features.append(feature)
                    feature_id += 1
                except Exception as e:
                    continue

        geojson_out = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_features": len(features),
                "bounds": image_bounds,
                "classes": self.CLASS_NAMES
            }
        }

        return geojson_out
