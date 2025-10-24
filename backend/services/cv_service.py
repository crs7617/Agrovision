"""
Lightweight Field Detection Service (No YOLO - Simple CV)
Detects agricultural field boundaries using traditional computer vision
"""
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FieldDetector:
    """Simple contour-based field detection (no deep learning)"""
    
    def __init__(self):
        """Initialize detector - no model download needed!"""
        logger.info("Lightweight field detector initialized")
    
    def multispectral_to_rgb(self, image_array: np.ndarray) -> np.ndarray:
        """
        Convert multispectral image to RGB
        Args:
            image_array: Multispectral numpy array (bands, height, width)
        Returns:
            RGB image (height, width, 3)
        """
        if image_array.ndim == 3 and image_array.shape[0] >= 3:
            rgb = np.stack([
                image_array[2],  # Red
                image_array[1],  # Green
                image_array[0]   # Blue
            ], axis=-1)
            
            # Normalize to 0-255
            rgb = ((rgb - rgb.min()) / (rgb.max() - rgb.min()) * 255).astype(np.uint8)
            return rgb
        else:
            # Single channel or invalid - just normalize
            if image_array.ndim == 2:
                img = ((image_array - image_array.min()) / 
                      (image_array.max() - image_array.min()) * 255).astype(np.uint8)
                return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            raise ValueError(f"Invalid image shape: {image_array.shape}")
    
    def detect_field_boundaries(
        self, 
        image_array: np.ndarray,
        min_area: int = 1000
    ) -> Dict:
        """
        Detect field boundaries using simple edge detection + contours
        Args:
            image_array: Multispectral or RGB image array
            min_area: Minimum contour area to consider
        Returns:
            Dictionary with bounding boxes and metadata
        """
        try:
            # Convert to RGB if needed
            if image_array.ndim == 3 and image_array.shape[0] < 10:
                rgb_image = self.multispectral_to_rgb(image_array)
            else:
                rgb_image = image_array
            
            # Convert to grayscale
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter and convert to bounding boxes
            detections = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    detection = {
                        "bbox": [x, y, x + w, y + h],
                        "confidence": min(area / (gray.shape[0] * gray.shape[1]), 1.0),
                        "class_id": 0,
                        "class_name": "field",
                        "area": int(area)
                    }
                    detections.append(detection)
            
            return {
                "success": True,
                "num_detections": len(detections),
                "detections": detections,
                "image_shape": rgb_image.shape
            }
        
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "num_detections": 0,
                "detections": []
            }
    
    def visualize_detections(
        self,
        image_array: np.ndarray,
        detections: List[Dict],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """Draw bounding boxes on image"""
        # Convert to RGB if needed
        if image_array.ndim == 3 and image_array.shape[0] < 10:
            annotated = self.multispectral_to_rgb(image_array).copy()
        else:
            annotated = image_array.copy()
        
        # Draw each detection
        for det in detections:
            bbox = det["bbox"]
            conf = det["confidence"]
            
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            label = f"Field: {conf:.2f}"
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(output_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
        
        return annotated
