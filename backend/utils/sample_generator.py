try:
    import cv2
except Exception:
    cv2 = None
import numpy as np
import os
from PIL import Image, ImageDraw

def generate_synthetic_drone_image(output_path, survey_year=2025, width=600, height=600):
    """
    Generates a realistic synthetic aerial drone ortho-photo with buildings, roads, water, and rooftops.
    If survey_year == 2026, includes realistic urban growth (new buildings, modified roofs, extra road extensions).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Base background: Green field / terrain
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = [45, 110, 50] # RGB dark green terrain

    # Add subtle ground texture noise
    noise = np.random.randint(-15, 15, (height, width, 3), dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    if cv2 is not None:
        # 1. Draw Water Body (Lake / River) - Blue
        cv2.ellipse(img, (120, 480), (90, 60), 30, 0, 360, (20, 100, 220), -1)

        # 2. Draw Main Asphalt Road Network - Grey
        cv2.line(img, (0, 300), (600, 300), (90, 95, 100), 28)
        cv2.line(img, (280, 0), (280, 600), (90, 95, 100), 22)
        # White road lane markings
        for x in range(10, 600, 40):
            cv2.line(img, (x, 300), (x + 20, 300), (240, 240, 240), 2)

        # 3. Draw Baseline 2025 Buildings (Red / Terracotta / Bright Rooftops)
        buildings_2025 = [
            (40, 40, 140, 120, (210, 80, 50)),
            (160, 40, 240, 110, (230, 220, 210)),
            (340, 50, 460, 150, (180, 70, 40)),
            (50, 160, 130, 240, (190, 195, 200)),
            (330, 340, 430, 420, (220, 90, 60)),
            (460, 340, 560, 450, (240, 240, 240))
        ]

        for x1, y1, x2, y2, color in buildings_2025:
            cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (40, 40, 40), 2)

        if survey_year == 2026:
            cv2.rectangle(img, (480, 40), (570, 130), (235, 110, 40), -1)
            cv2.rectangle(img, (480, 40), (570, 130), (40, 40, 40), 2)

            cv2.rectangle(img, (40, 350), (140, 420), (210, 75, 45), -1)
            cv2.rectangle(img, (40, 350), (140, 420), (40, 40, 40), 2)

            cv2.rectangle(img, (50, 160), (130, 240), (50, 115, 55), -1)

            cv2.rectangle(img, (340, 50), (475, 185), (245, 240, 235), -1)
            cv2.rectangle(img, (340, 50), (475, 185), (40, 40, 40), 2)

        cv2.imwrite(output_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    else:
        # Fallback to PIL ImageDraw
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.ellipse([30, 420, 210, 540], fill=(20, 100, 220))
        draw.line([(0, 300), (600, 300)], fill=(90, 95, 100), width=28)
        draw.line([(280, 0), (280, 600)], fill=(90, 95, 100), width=22)

        buildings_2025 = [
            (40, 40, 140, 120, (210, 80, 50)),
            (160, 40, 240, 110, (230, 220, 210)),
            (340, 50, 460, 150, (180, 70, 40)),
            (50, 160, 130, 240, (190, 195, 200)),
            (330, 340, 430, 420, (220, 90, 60)),
            (460, 340, 560, 450, (240, 240, 240))
        ]
        for x1, y1, x2, y2, color in buildings_2025:
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=(40, 40, 40), width=2)

        if survey_year == 2026:
            draw.rectangle([480, 40, 570, 130], fill=(235, 110, 40), outline=(40, 40, 40), width=2)
            draw.rectangle([40, 350, 140, 420], fill=(210, 75, 45), outline=(40, 40, 40), width=2)
            draw.rectangle([50, 160, 130, 240], fill=(50, 115, 55))
            draw.rectangle([340, 50, 475, 185], fill=(245, 240, 235), outline=(40, 40, 40), width=2)

        pil_img.save(output_path)

    return output_path

