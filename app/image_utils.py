from pathlib import Path
from PIL import Image, ImageOps

OPTIMIZED_DIR = Path("uploads/cars/optimized")

def create_optimized_image(original_path: Path, image_id: str) -> Path:
    OPTIMIZED_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OPTIMIZED_DIR / f"{image_id}.webp"

    with Image.open(original_path) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((1600, 1600))
        image = image.convert("RGB")
        image.save(output_path, "WEBP", quality=80, method=6)

    return output_path
