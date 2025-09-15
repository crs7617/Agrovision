"""
Fast Multispectral Images Downloader - Based on working method
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

try:
    from sentinelhub import (
        SHConfig, BBox, CRS, MimeType, DataCollection,
        SentinelHubRequest
    )
    SENTINELHUB_AVAILABLE = True
except ImportError:
    SENTINELHUB_AVAILABLE = False
    print("❌ Sentinel Hub not available")

# Expanded locations for 60 total images across India's agricultural regions
WORKING_LOCATIONS = [
    # Northern India - Punjab, Haryana, UP, Delhi
    {"name": "Punjab_Ludhiana", "bbox": [75.8, 30.9, 76.0, 31.1], "crop": "rice_wheat"},
    {"name": "Punjab_Amritsar", "bbox": [74.7, 31.5, 74.9, 31.7], "crop": "wheat"},
    {"name": "Punjab_Jalandhar", "bbox": [75.5, 31.2, 75.7, 31.4], "crop": "rice"},
    {"name": "Punjab_Patiala", "bbox": [76.3, 30.2, 76.5, 30.4], "crop": "wheat_rice"},
    {"name": "Punjab_Bathinda", "bbox": [74.9, 30.1, 75.1, 30.3], "crop": "cotton"},
    {"name": "Haryana_Panipat", "bbox": [76.9, 29.3, 77.1, 29.5], "crop": "wheat"},
    {"name": "Haryana_Karnal", "bbox": [76.9, 29.6, 77.1, 29.8], "crop": "wheat_rice"},
    {"name": "Haryana_Hisar", "bbox": [75.6, 29.1, 75.8, 29.3], "crop": "wheat"},
    {"name": "Haryana_Rohtak", "bbox": [76.5, 28.8, 76.7, 29.0], "crop": "wheat"},
    {"name": "Haryana_Gurgaon", "bbox": [77.0, 28.4, 77.2, 28.6], "crop": "wheat"},
    {"name": "UP_Kanpur", "bbox": [80.2, 26.3, 80.4, 26.5], "crop": "wheat"},
    {"name": "UP_Lucknow", "bbox": [80.8, 26.7, 81.0, 26.9], "crop": "wheat_rice"},
    {"name": "UP_Agra", "bbox": [78.0, 27.1, 78.2, 27.3], "crop": "wheat"},
    {"name": "UP_Meerut", "bbox": [77.6, 28.9, 77.8, 29.1], "crop": "sugarcane"},
    {"name": "UP_Varanasi", "bbox": [82.9, 25.2, 83.1, 25.4], "crop": "rice_wheat"},
    
    # Western India - Maharashtra, Gujarat, Rajasthan
    {"name": "Maharashtra_Pune", "bbox": [73.7, 18.4, 73.9, 18.6], "crop": "cotton"},
    {"name": "Maharashtra_Nashik", "bbox": [73.7, 19.9, 73.9, 20.1], "crop": "cotton"},
    {"name": "Maharashtra_Aurangabad", "bbox": [75.2, 19.8, 75.4, 20.0], "crop": "cotton"},
    {"name": "Maharashtra_Nagpur", "bbox": [79.0, 21.1, 79.2, 21.3], "crop": "cotton"},
    {"name": "Maharashtra_Kolhapur", "bbox": [74.1, 16.6, 74.3, 16.8], "crop": "sugarcane"},
    {"name": "Gujarat_Ahmedabad", "bbox": [72.4, 23.0, 72.6, 23.2], "crop": "cotton"},
    {"name": "Gujarat_Rajkot", "bbox": [70.7, 22.2, 70.9, 22.4], "crop": "cotton"},
    {"name": "Gujarat_Vadodara", "bbox": [73.1, 22.2, 73.3, 22.4], "crop": "cotton"},
    {"name": "Gujarat_Surat", "bbox": [72.7, 21.1, 72.9, 21.3], "crop": "cotton"},
    {"name": "Gujarat_Bhavnagar", "bbox": [72.1, 21.7, 72.3, 21.9], "crop": "cotton"},
    {"name": "Rajasthan_Jaipur", "bbox": [75.7, 26.8, 75.9, 27.0], "crop": "wheat"},
    {"name": "Rajasthan_Bharatpur", "bbox": [77.4, 27.1, 77.6, 27.3], "crop": "wheat"},
    {"name": "Rajasthan_Alwar", "bbox": [76.5, 27.5, 76.7, 27.7], "crop": "wheat"},
    {"name": "Rajasthan_Kota", "bbox": [75.8, 25.1, 76.0, 25.3], "crop": "wheat"},
    {"name": "Rajasthan_Udaipur", "bbox": [73.6, 24.5, 73.8, 24.7], "crop": "wheat"},
    
    # Southern India - Karnataka, Tamil Nadu, Andhra Pradesh, Telangana
    {"name": "Karnataka_Bangalore", "bbox": [77.4, 12.8, 77.6, 13.0], "crop": "cereals"},
    {"name": "Karnataka_Mysore", "bbox": [76.5, 12.2, 76.7, 12.4], "crop": "sugarcane"},
    {"name": "Karnataka_Hubli", "bbox": [75.1, 15.3, 75.3, 15.5], "crop": "cotton"},
    {"name": "Karnataka_Belgaum", "bbox": [74.4, 15.8, 74.6, 16.0], "crop": "cotton"},
    {"name": "Karnataka_Gulbarga", "bbox": [76.8, 17.3, 77.0, 17.5], "crop": "cotton"},
    {"name": "TamilNadu_Chennai", "bbox": [80.1, 13.0, 80.3, 13.2], "crop": "rice"},
    {"name": "TamilNadu_Coimbatore", "bbox": [76.9, 10.9, 77.1, 11.1], "crop": "rice"},
    {"name": "TamilNadu_Madurai", "bbox": [78.0, 9.9, 78.2, 10.1], "crop": "rice"},
    {"name": "TamilNadu_Salem", "bbox": [78.1, 11.6, 78.3, 11.8], "crop": "rice"},
    {"name": "TamilNadu_Trichy", "bbox": [78.6, 10.7, 78.8, 10.9], "crop": "rice"},
    {"name": "AP_Hyderabad", "bbox": [78.3, 17.3, 78.5, 17.5], "crop": "rice"},
    {"name": "AP_Vijayawada", "bbox": [80.5, 16.4, 80.7, 16.6], "crop": "rice"},
    {"name": "AP_Visakhapatnam", "bbox": [83.2, 17.6, 83.4, 17.8], "crop": "rice"},
    {"name": "AP_Tirupati", "bbox": [79.3, 13.6, 79.5, 13.8], "crop": "rice"},
    {"name": "AP_Guntur", "bbox": [80.4, 16.2, 80.6, 16.4], "crop": "cotton"},
    
    # Eastern India - West Bengal, Bihar, Odisha
    {"name": "WestBengal_Kolkata", "bbox": [88.2, 22.4, 88.4, 22.6], "crop": "rice"},
    {"name": "WestBengal_Burdwan", "bbox": [87.8, 23.2, 88.0, 23.4], "crop": "rice"},
    {"name": "WestBengal_Durgapur", "bbox": [87.2, 23.4, 87.4, 23.6], "crop": "rice"},
    {"name": "WestBengal_Siliguri", "bbox": [88.3, 26.6, 88.5, 26.8], "crop": "rice"},
    {"name": "WestBengal_Krishnanagar", "bbox": [88.4, 23.4, 88.6, 23.6], "crop": "rice"},
    {"name": "Bihar_Patna", "bbox": [85.0, 25.5, 85.2, 25.7], "crop": "rice_wheat"},
    {"name": "Bihar_Gaya", "bbox": [84.9, 24.7, 85.1, 24.9], "crop": "wheat"},
    {"name": "Bihar_Bhagalpur", "bbox": [87.0, 25.2, 87.2, 25.4], "crop": "rice"},
    {"name": "Bihar_Muzaffarpur", "bbox": [85.3, 26.1, 85.5, 26.3], "crop": "rice"},
    {"name": "Bihar_Darbhanga", "bbox": [85.8, 26.1, 86.0, 26.3], "crop": "rice"},
    
    # Central India - Madhya Pradesh, Chhattisgarh
    {"name": "MP_Bhopal", "bbox": [77.3, 23.2, 77.5, 23.4], "crop": "wheat"},
    {"name": "MP_Indore", "bbox": [75.8, 22.7, 76.0, 22.9], "crop": "wheat"},
    {"name": "MP_Gwalior", "bbox": [78.1, 26.2, 78.3, 26.4], "crop": "wheat"},
    {"name": "MP_Jabalpur", "bbox": [79.9, 23.1, 80.1, 23.3], "crop": "wheat"},
    {"name": "MP_Ujjain", "bbox": [75.7, 23.1, 75.9, 23.3], "crop": "wheat"},
    {"name": "Chhattisgarh_Raipur", "bbox": [81.5, 21.2, 81.7, 21.4], "crop": "rice"},
    {"name": "Chhattisgarh_Bilaspur", "bbox": [82.1, 22.0, 82.3, 22.2], "crop": "rice"},
    {"name": "Chhattisgarh_Durg", "bbox": [81.2, 21.1, 81.4, 21.3], "crop": "rice"},
    {"name": "Chhattisgarh_Korba", "bbox": [82.6, 22.3, 82.8, 22.5], "crop": "rice"},
    {"name": "Chhattisgarh_Raigarh", "bbox": [83.3, 21.8, 83.5, 22.0], "crop": "rice"}
]

class FastMultispectralDownloader:
    def __init__(self):
        load_dotenv()
        
        self.output_dir = Path("fast_multispectral")
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup Sentinel Hub
        config = SHConfig()
        config.sh_client_id = os.getenv('SH_CLIENT_ID')
        config.sh_client_secret = os.getenv('SH_CLIENT_SECRET')
        config.save()
        self.config = config
        print("✅ Sentinel Hub configured")
        
    def download_fast_multispectral(self):
        """Download 60 multispectral images fast using working method"""
        print("🚀 FAST DOWNLOAD: 60 MULTISPECTRAL IMAGES")
        print("⚡ Using proven working method")
        print("🗺️ Comprehensive coverage across all Indian agricultural regions")
        print(f"📂 Output: {self.output_dir}")
        
        # Working evalscript - same as successful test
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: ["B02", "B03", "B04", "B08", "B11"],
                output: { bands: 5 }
            };
        }
        function evaluatePixel(sample) {
            return [sample.B02, sample.B03, sample.B04, sample.B08, sample.B11];
        }
        """
        
        successful = 0
        total_size_mb = 0
        
        for i, location in enumerate(WORKING_LOCATIONS):
            if successful >= 60:  # Download 60 images
                break
                
            print(f"\n🔄 {successful+1}/60 - {location['name']}")
            print(f"   📍 BBox: {location['bbox']}")
            print(f"   🌾 Crop: {location['crop']}")
            
            try:
                bbox = BBox(location['bbox'], crs=CRS.WGS84)
                
                # Use recent date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=60)  # 60 days back
                
                request = SentinelHubRequest(
                    evalscript=evalscript,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L2A,
                            time_interval=(start_date, end_date),
                            maxcc=0.9  # Allow high cloud cover
                        )
                    ],
                    responses=[
                        SentinelHubRequest.output_response('default', MimeType.TIFF)
                    ],
                    bbox=bbox,
                    size=(256, 256),  # Optimized size
                    config=self.config
                )
                
                print("   ⬇️ Downloading...")
                response = request.get_data()
                
                if response and len(response) > 0 and hasattr(response[0], 'shape'):
                    # Save multispectral data
                    filename = f"{location['name']}_multispectral.npy"
                    np.save(self.output_dir / filename, response[0])
                    
                    # Calculate NDVI
                    red = response[0][:, :, 2].astype(float)  # B04
                    nir = response[0][:, :, 3].astype(float)  # B08
                    ndvi = (nir - red) / (nir + red + 0.001)
                    np.save(self.output_dir / f"{location['name']}_ndvi.npy", ndvi)
                    
                    # Calculate size
                    size_mb = response[0].nbytes / (1024*1024)
                    total_size_mb += size_mb
                    
                    # Save metadata
                    metadata = {
                        "name": location['name'],
                        "bands": ["B02(Blue)", "B03(Green)", "B04(Red)", "B08(NIR)", "B11(SWIR1)"],
                        "shape": response[0].shape,
                        "size_mb": round(size_mb, 2),
                        "ndvi_mean": float(np.nanmean(ndvi)),
                        "vegetation_pixels": int(np.sum(ndvi > 0.3)),
                        "crop_type": location['crop'],
                        "bbox": location['bbox'],
                        "download_time": datetime.now().isoformat()
                    }
                    
                    with open(self.output_dir / f"{location['name']}_metadata.json", 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    successful += 1
                    print(f"   ✅ SUCCESS!")
                    print(f"   📊 Shape: {response[0].shape}")
                    print(f"   💾 Size: {size_mb:.1f} MB")
                    print(f"   💚 NDVI: {metadata['ndvi_mean']:.3f}")
                    print(f"   🎯 Progress: {successful}/60")
                    print(f"   📦 Total: {total_size_mb:.1f} MB")
                    
                else:
                    print("   ❌ No data for this location")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                
        print(f"\n🎉 DOWNLOAD COMPLETE!")
        print(f"✅ Successfully downloaded: {successful} multispectral images")
        print(f"💾 Total size: {total_size_mb:.1f} MB ({total_size_mb/1024:.2f} GB)")
        print(f"📁 Location: {self.output_dir}")
        
        if total_size_mb <= 2048:
            print(f"✅ Size target met: {total_size_mb:.1f} MB ≤ 2 GB")
        
        if successful >= 30:  # Success if we get at least 30 images
            print("🔥 Ready for multispectral preprocessing!")
            return True
        else:
            print("⚠️ Low success rate")
            return False

def main():
    downloader = FastMultispectralDownloader()
    success = downloader.download_fast_multispectral()
    
    if success:
        print("\n🚀 Next: Create multispectral preprocessor")

if __name__ == "__main__":
    main()