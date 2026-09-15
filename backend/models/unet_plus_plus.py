import numpy as np


class GeospatialSegmentationPipeline:
    """Lightweight segmentation pipeline for serverless deployment.

    The prototype does not ship trained model weights, so the deployed behavior
    is the existing spectral segmentation fallback. Keeping it NumPy-only avoids
    bundling PyTorch, which is too large for a Vercel function.
    """

    def __init__(self, weights_path=None, num_classes=5):
        self.device = "cpu (spectral fallback)"
        self.num_classes = num_classes

    def predict_mask(self, image_np):
        """Return class labels for an RGB image normalized to [0, 1]."""
        img_255 = np.clip(image_np * 255, 0, 255).astype(np.uint8)
        r, g, b = (
            img_255[:, :, 0].astype(np.int16),
            img_255[:, :, 1].astype(np.int16),
            img_255[:, :, 2].astype(np.int16),
        )

        enhanced_mask = np.zeros(image_np.shape[:2], dtype=np.uint8)

        water_cond = (b > r + 15) & (b > g) & (b > 60)
        road_cond = (
            (np.abs(r - g) < 25)
            & (np.abs(g - b) < 25)
            & (r > 70)
            & (r < 180)
            & ~water_cond
        )
        roof_cond = (
            ((r > g + 20) & (r > b + 20))
            | ((r > 200) & (g > 200) & (b > 200))
        )
        building_cond = (
            ((r > 160) | (g > 160) | (b > 160))
            & ~water_cond
            & ~road_cond
            & ~roof_cond
        )

        enhanced_mask[water_cond] = 3
        enhanced_mask[road_cond] = 2
        enhanced_mask[roof_cond] = 4
        enhanced_mask[building_cond] = 1
        return enhanced_mask
