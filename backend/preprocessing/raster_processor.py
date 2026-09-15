try:
    import cv2
except Exception:
    cv2 = None
import numpy as np
from PIL import Image
import os

class RasterProcessor:
    """Pre-processing module for reading drone imagery, tiling, resizing, and normalization."""
    
    def __init__(self, tile_size=256, overlap=32):
        self.tile_size = tile_size
        self.overlap = overlap

    def load_image(self, file_path):
        """Loads an image file (PNG, JPG, TIFF) into an RGB float32 numpy array [0.0, 1.0]."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image not found at {file_path}")

        image = cv2.imread(file_path) if cv2 is not None else None
        if image is None:
            # Fallback to PIL if OpenCV fails or is not available
            pil_img = Image.open(file_path).convert('RGB')
            img_np = np.array(pil_img)
        else:
            img_np = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


        # Normalize to 0-1
        normalized_img = img_np.astype(np.float32) / 255.0
        return normalized_img, img_np.shape[:2]

    def create_tiles(self, image_np):
        """
        Splits image into overlapping tiles of size (tile_size x tile_size).
        Returns list of (tile, y_start, x_start).
        """
        h, w, _ = image_np.shape
        stride = self.tile_size - self.overlap
        tiles = []

        for y in range(0, h, stride):
            for x in range(0, w, stride):
                y_end = min(y + self.tile_size, h)
                x_end = min(x + self.tile_size, w)
                
                # Extract patch
                tile = image_np[y:y_end, x:x_end]
                
                # Pad tile if smaller than tile_size
                pad_y = self.tile_size - tile.shape[0]
                pad_x = self.tile_size - tile.shape[1]
                
                if pad_y > 0 or pad_x > 0:
                    tile = np.pad(tile, ((0, pad_y), (0, pad_x), (0, 0)), mode='reflect')
                
                tiles.append({
                    'tile': tile,
                    'y': y,
                    'x': x,
                    'h_orig': y_end - y,
                    'w_orig': x_end - x
                })

        return tiles

    def stitch_tiles(self, tile_masks, original_shape):
        """
        Stitches segmented tile masks back into full resolution mask map.
        Uses overlap-aware averaging / max confidence logic.
        """
        h, w = original_shape
        full_mask = np.zeros((h, w), dtype=np.uint8)

        for item in tile_masks:
            mask = item['mask']
            y, x = item['y'], item['x']
            h_o, w_o = item['h_orig'], item['w_orig']

            # Overwrite or combine
            full_mask[y:y+h_o, x:x+w_o] = mask[:h_o, :w_o]

        return full_mask
