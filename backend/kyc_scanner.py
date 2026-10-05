import os
import sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageChops, ImageEnhance

# Ensure root folder is accessible for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def error_level_analysis(image_path: Path, quality: int = 90) -> float:
    """
    Measures digital recompression error delta (ELA).
    Synthetic spliced images show abnormal compression variances.
    """
    try:
        original = Image.open(image_path).convert('RGB')
        temp_path = image_path.parent / f"_temp_ela_{image_path.name}.jpg"
        original.save(temp_path, 'JPEG', quality=quality)
        
        resaved = Image.open(temp_path)
        ela_diff = ImageChops.difference(original, resaved)
        
        extrema = ela_diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        
        scale = 255.0 / max_diff
        enhanced_diff = ImageEnhance.Brightness(ela_diff).enhance(scale)
        
        if temp_path.exists():
            temp_path.unlink()
            
        mean_diff = float(np.array(enhanced_diff).mean())
        # Normalize to a 0.0 - 1.0 boundary score
        return float(min(1.0, max(0.0, mean_diff / 60.0)))
    except Exception as err:
        print(f"[!] ELA calculation warning: {err}")
        return 0.50

def high_frequency_noise_variance(image_path: Path) -> float:
    """
    Calculates Laplacian kernel variance to detect diffusion model smoothing.
    Real mobile camera sensors produce natural Gaussian grain.
    """
    try:
        img_gray = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img_gray is None:
            return 0.50
        
        laplacian_var = float(cv2.Laplacian(img_gray, cv2.CV_64F).var())
        
        # Abnormally flat or smoothed Laplacian variance indicates diffusion generation
        if laplacian_var < 45.0:
            return 0.92
        elif laplacian_var > 450.0:
            return 0.15
        else:
            return float(round(1.0 - (laplacian_var / 450.0), 3))
    except Exception as err:
        print(f"[!] Noise variance warning: {err}")
        return 0.50

def analyze_kyc_document(image_path_str: str) -> dict:
    """
    Primary interface for KYC image evaluation.
    Returns composite synthetic_image_score in [0.0, 1.0].
    """
    target_path = Path(image_path_str)
    if not target_path.exists():
        return {
            "synthetic_image_score": 0.0,
            "status": "FILE_NOT_FOUND",
            "is_synthetic_suspect": False
        }

    ela_score = error_level_analysis(target_path)
    noise_score = high_frequency_noise_variance(target_path)
    
    # Weighted composite index
    composite_score = round((0.55 * ela_score) + (0.45 * noise_score), 3)
    is_suspect = composite_score >= 0.65

    return {
        "file_name": target_path.name,
        "synthetic_image_score": composite_score,
        "ela_metric": round(ela_score, 3),
        "noise_metric": round(noise_score, 3),
        "is_synthetic_suspect": is_suspect
    }

if __name__ == "__main__":
    # Create a dummy image to test execution in standalone mode
    test_dir = Path("data") / "test_samples"
    test_dir.mkdir(parents=True, exist_ok=True)
    sample_img_path = test_dir / "sample_id.jpg"

    # Generate a lightweight gradient test pattern
    dummy_array = np.zeros((300, 450, 3), dtype=np.uint8)
    cv2.putText(dummy_array, "TEST ID CARD", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imwrite(str(sample_img_path), dummy_array)

    print(f"[*] Analyzing sample card: {sample_img_path}")
    result = analyze_kyc_document(str(sample_img_path))
    print(f"[*] KYC Scanner Results:")
    print(f"    - Synthetic Score: {result['synthetic_image_score']}")
    print(f"    - Diffusion Suspect: {result['is_synthetic_suspect']}")
    print(f"    - ELA Metric: {result['ela_metric']}")
    print(f"    - Noise Metric: {result['noise_metric']}")