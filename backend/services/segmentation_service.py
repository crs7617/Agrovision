"""
Lightweight Health Zone Segmentation (No U-Net - Simple Thresholding)
Segments crop health zones based on NDVI values using color-coded thresholds
"""
import numpy as np
import cv2
from typing import Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HealthZoneSegmenter:
    """Simple threshold-based health zone segmentation (no deep learning)"""
    
    # NDVI thresholds for health zones
    THRESHOLDS = {
        "excellent": 0.6,
        "good": 0.4,
        "stressed": 0.2,
        "poor": 0.0
    }
    
    # Color coding for visualization (RGB format)
    COLORS = {
        "excellent": (0, 255, 0),      # Green
        "good": (255, 255, 0),          # Yellow
        "stressed": (255, 165, 0),      # Orange
        "poor": (255, 0, 0)             # Red
    }
    
    def __init__(self):
        """Initialize segmenter - no model needed!"""
        logger.info("Lightweight health zone segmenter initialized")
    
    def ndvi_to_zones(self, ndvi_array: np.ndarray) -> np.ndarray:
        """
        Threshold NDVI into health zones
        Args:
            ndvi_array: NDVI values (height, width)
        Returns:
            Zone labels (height, width) with values 0-3
        """
        zones = np.zeros_like(ndvi_array, dtype=np.uint8)
        
        # Classify each pixel
        zones[ndvi_array >= self.THRESHOLDS["excellent"]] = 0  # Excellent
        zones[(ndvi_array >= self.THRESHOLDS["good"]) & 
              (ndvi_array < self.THRESHOLDS["excellent"])] = 1  # Good
        zones[(ndvi_array >= self.THRESHOLDS["stressed"]) & 
              (ndvi_array < self.THRESHOLDS["good"])] = 2       # Stressed
        zones[ndvi_array < self.THRESHOLDS["stressed"]] = 3    # Poor
        
        return zones
    
    def segment_health_zones(self, ndvi_array: np.ndarray) -> Dict:
        """
        Segment NDVI into health zones
        Args:
            ndvi_array: NDVI values (height, width)
        Returns:
            Dictionary with mask and statistics
        """
        try:
            # Simple threshold-based segmentation
            zone_mask = self.ndvi_to_zones(ndvi_array)
            
            # Calculate zone statistics
            total_pixels = zone_mask.size
            stats = {
                "excellent": {
                    "pixels": int(np.sum(zone_mask == 0)),
                    "percentage": float(np.sum(zone_mask == 0) / total_pixels * 100)
                },
                "good": {
                    "pixels": int(np.sum(zone_mask == 1)),
                    "percentage": float(np.sum(zone_mask == 1) / total_pixels * 100)
                },
                "stressed": {
                    "pixels": int(np.sum(zone_mask == 2)),
                    "percentage": float(np.sum(zone_mask == 2) / total_pixels * 100)
                },
                "poor": {
                    "pixels": int(np.sum(zone_mask == 3)),
                    "percentage": float(np.sum(zone_mask == 3) / total_pixels * 100)
                }
            }
            
            return {
                "success": True,
                "mask": zone_mask,
                "statistics": stats,
                "shape": zone_mask.shape
            }
        
        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "mask": None,
                "statistics": {}
            }
    
    def create_color_mask(self, zone_mask: np.ndarray) -> np.ndarray:
        """
        Convert zone labels to color-coded RGB mask
        Args:
            zone_mask: Zone labels (height, width)
        Returns:
            RGB color mask (height, width, 3)
        """
        h, w = zone_mask.shape
        color_mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Apply colors to each zone
        color_mask[zone_mask == 0] = self.COLORS["excellent"]
        color_mask[zone_mask == 1] = self.COLORS["good"]
        color_mask[zone_mask == 2] = self.COLORS["stressed"]
        color_mask[zone_mask == 3] = self.COLORS["poor"]
        
        return color_mask
    
    def overlay_mask(
        self,
        original_image: np.ndarray,
        zone_mask: np.ndarray,
        alpha: float = 0.5
    ) -> np.ndarray:
        """Overlay color-coded mask on original image"""
        color_mask = self.create_color_mask(zone_mask)
        
        if original_image.shape != color_mask.shape:
            original_image = cv2.resize(original_image, (color_mask.shape[1], color_mask.shape[0]))
        
        blended = cv2.addWeighted(original_image, 1 - alpha, color_mask, alpha, 0)
        return blended
    
    def save_mask_with_legend(
        self,
        zone_mask: np.ndarray,
        output_path: str,
        statistics: Dict
    ):
        """Save color-coded mask with legend"""
        color_mask = self.create_color_mask(zone_mask)
        
        # Add legend
        legend_height = 150
        h, w = color_mask.shape[:2]
        canvas = np.ones((h + legend_height, w, 3), dtype=np.uint8) * 255
        canvas[:h, :] = color_mask
        
        # Draw legend
        y_offset = h + 30
        legend_items = [
            ("Excellent (>0.6)", self.COLORS["excellent"], statistics["excellent"]["percentage"]),
            ("Good (0.4-0.6)", self.COLORS["good"], statistics["good"]["percentage"]),
            ("Stressed (0.2-0.4)", self.COLORS["stressed"], statistics["stressed"]["percentage"]),
            ("Poor (<0.2)", self.COLORS["poor"], statistics["poor"]["percentage"])
        ]
        
        for i, (label, color, pct) in enumerate(legend_items):
            x = 20 + (i % 2) * (w // 2)
            y = y_offset + (i // 2) * 40
            
            cv2.rectangle(canvas, (x, y - 15), (x + 30, y + 5), color, -1)
            text = f"{label}: {pct:.1f}%"
            cv2.putText(canvas, text, (x + 40, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Save
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))
        logger.info(f"Segmentation mask saved to {output_path}")
    
    def ndvi_to_zones(self, ndvi_array: np.ndarray) -> np.ndarray:
        """
        Threshold NDVI into health zones
        Args:
            ndvi_array: NDVI values (height, width)
        Returns:
            Zone labels (height, width) with values 0-3
        """
        zones = np.zeros_like(ndvi_array, dtype=np.uint8)
        
        # Classify each pixel
        zones[ndvi_array >= self.THRESHOLDS["excellent"]] = 0  # Excellent
        zones[(ndvi_array >= self.THRESHOLDS["good"]) & 
              (ndvi_array < self.THRESHOLDS["excellent"])] = 1  # Good
        zones[(ndvi_array >= self.THRESHOLDS["stressed"]) & 
              (ndvi_array < self.THRESHOLDS["good"])] = 2       # Stressed
        zones[ndvi_array < self.THRESHOLDS["stressed"]] = 3    # Poor
        
        return zones
    
    def segment_health_zones(self, ndvi_array: np.ndarray) -> Dict:
        """
        Segment NDVI into health zones
        Args:
            ndvi_array: NDVI values (height, width)
        Returns:
            Dictionary with mask and statistics
        """
        try:
            # Threshold-based segmentation (simple approach for free tier)
            zone_mask = self.ndvi_to_zones(ndvi_array)
            
            # Calculate zone statistics
            total_pixels = zone_mask.size
            stats = {
                "excellent": {
                    "pixels": int(np.sum(zone_mask == 0)),
                    "percentage": float(np.sum(zone_mask == 0) / total_pixels * 100)
                },
                "good": {
                    "pixels": int(np.sum(zone_mask == 1)),
                    "percentage": float(np.sum(zone_mask == 1) / total_pixels * 100)
                },
                "stressed": {
                    "pixels": int(np.sum(zone_mask == 2)),
                    "percentage": float(np.sum(zone_mask == 2) / total_pixels * 100)
                },
                "poor": {
                    "pixels": int(np.sum(zone_mask == 3)),
                    "percentage": float(np.sum(zone_mask == 3) / total_pixels * 100)
                }
            }
            
            return {
                "success": True,
                "mask": zone_mask,
                "statistics": stats,
                "shape": zone_mask.shape
            }
        
        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "mask": None,
                "statistics": {}
            }
    
    def create_color_mask(self, zone_mask: np.ndarray) -> np.ndarray:
        """
        Convert zone labels to color-coded RGB mask
        Args:
            zone_mask: Zone labels (height, width)
        Returns:
            RGB color mask (height, width, 3)
        """
        h, w = zone_mask.shape
        color_mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Apply colors to each zone
        color_mask[zone_mask == 0] = self.COLORS["excellent"][::-1]  # Convert BGR to RGB
        color_mask[zone_mask == 1] = self.COLORS["good"][::-1]
        color_mask[zone_mask == 2] = self.COLORS["stressed"][::-1]
        color_mask[zone_mask == 3] = self.COLORS["poor"][::-1]
        
        return color_mask
    
    def overlay_mask(
        self,
        original_image: np.ndarray,
        zone_mask: np.ndarray,
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Overlay color-coded mask on original image
        Args:
            original_image: Original RGB image
            zone_mask: Zone labels
            alpha: Transparency (0-1)
        Returns:
            Blended image
        """
        # Create color mask
        color_mask = self.create_color_mask(zone_mask)
        
        # Ensure original image is RGB
        if original_image.shape != color_mask.shape:
            original_image = cv2.resize(original_image, (color_mask.shape[1], color_mask.shape[0]))
        
        # Blend
        blended = cv2.addWeighted(original_image, 1 - alpha, color_mask, alpha, 0)
        
        return blended
    
    def save_mask_with_legend(
        self,
        zone_mask: np.ndarray,
        output_path: str,
        statistics: Dict
    ):
        """
        Save color-coded mask with legend
        Args:
            zone_mask: Zone labels
            output_path: Where to save the image
            statistics: Zone statistics for legend
        """
        # Create color mask
        color_mask = self.create_color_mask(zone_mask)
        
        # Add legend
        legend_height = 150
        h, w = color_mask.shape[:2]
        canvas = np.ones((h + legend_height, w, 3), dtype=np.uint8) * 255
        canvas[:h, :] = color_mask
        
        # Draw legend
        y_offset = h + 30
        legend_items = [
            ("Excellent (>0.6)", self.COLORS["excellent"][::-1], statistics["excellent"]["percentage"]),
            ("Good (0.4-0.6)", self.COLORS["good"][::-1], statistics["good"]["percentage"]),
            ("Stressed (0.2-0.4)", self.COLORS["stressed"][::-1], statistics["stressed"]["percentage"]),
            ("Poor (<0.2)", self.COLORS["poor"][::-1], statistics["poor"]["percentage"])
        ]
        
        for i, (label, color, pct) in enumerate(legend_items):
            x = 20 + (i % 2) * (w // 2)
            y = y_offset + (i // 2) * 40
            
            # Draw color box
            cv2.rectangle(canvas, (x, y - 15), (x + 30, y + 5), color, -1)
            
            # Draw text
            text = f"{label}: {pct:.1f}%"
            cv2.putText(canvas, text, (x + 40, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Save
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))
        logger.info(f"Segmentation mask saved to {output_path}")


def test_segmentation():
    """Test function for health zone segmentation"""
    segmenter = HealthZoneSegmenter()
    
    # Create dummy NDVI data
    ndvi = np.random.rand(256, 256).astype(np.float32)
    
    # Test segmentation
    results = segmenter.segment_health_zones(ndvi)
    print(f"Segmentation results: {results['statistics']}")
    
    # Save visualization
    if results["success"]:
        segmenter.save_mask_with_legend(
            results["mask"],
            "temp/test_segmentation.png",
            results["statistics"]
        )
    
    return results


if __name__ == "__main__":
    test_segmentation()
