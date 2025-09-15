#!/usr/bin/env python3
"""
AgroVision AI - Advanced Multispectral Preprocessor
==================================================
Comprehensive preprocessing pipeline for agricultural satellite imagery
with advanced vegetation indices and crop health analysis.

Author: AgroVision AI Team
Date: September 2025
"""

import numpy as np
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pandas as pd

class AgroVisionPreprocessor:
    """Advanced multispectral preprocessor for agricultural analysis"""
    
    def __init__(self, data_dir="fast_multispectral", output_dir="processed_agrovision"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "vegetation_indices").mkdir(exist_ok=True)
        (self.output_dir / "visualizations").mkdir(exist_ok=True)
        (self.output_dir / "statistics").mkdir(exist_ok=True)
        (self.output_dir / "analysis_reports").mkdir(exist_ok=True)
        
        print("🚀 AgroVision AI Multispectral Preprocessor Initialized")
        print(f"📂 Input: {self.data_dir}")
        print(f"📁 Output: {self.output_dir}")
    
    def load_multispectral_image(self, location_name):
        """Load multispectral image and metadata"""
        img_path = self.data_dir / f"{location_name}_multispectral.npy"
        meta_path = self.data_dir / f"{location_name}_metadata.json"
        
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {img_path}")
            
        # Load image (256, 256, 5) - [B02, B03, B04, B08, B11]
        img = np.load(img_path)
        
        # Load metadata
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
            
        return img, metadata
    
    def calculate_vegetation_indices(self, img):
        """Calculate comprehensive vegetation indices"""
        # Extract bands
        blue = img[:, :, 0].astype(np.float32)    # B02
        green = img[:, :, 1].astype(np.float32)   # B03  
        red = img[:, :, 2].astype(np.float32)     # B04
        nir = img[:, :, 3].astype(np.float32)     # B08
        swir1 = img[:, :, 4].astype(np.float32)   # B11
        
        # Avoid division by zero
        epsilon = 1e-8
        
        indices = {}
        
        # 1. NDVI - Normalized Difference Vegetation Index
        indices['NDVI'] = (nir - red) / (nir + red + epsilon)
        
        # 2. EVI - Enhanced Vegetation Index
        indices['EVI'] = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1 + epsilon)
        
        # 3. SAVI - Soil Adjusted Vegetation Index (L=0.5)
        L = 0.5
        indices['SAVI'] = ((nir - red) / (nir + red + L + epsilon)) * (1 + L)
        
        # 4. OSAVI - Optimized Soil Adjusted Vegetation Index
        indices['OSAVI'] = (nir - red) / (nir + red + 0.16 + epsilon)
        
        # 5. GNDVI - Green Normalized Difference Vegetation Index
        indices['GNDVI'] = (nir - green) / (nir + green + epsilon)
        
        # 6. CIG - Chlorophyll Index Green
        indices['CIG'] = (nir / green) - 1
        
        # 7. LAI - Leaf Area Index (empirical formula)
        indices['LAI'] = np.log((0.69 - indices['SAVI']) / 0.59) / 0.91
        indices['LAI'] = np.clip(indices['LAI'], 0, 10)  # Realistic LAI range
        
        # 8. NDWI - Normalized Difference Water Index
        indices['NDWI'] = (green - nir) / (green + nir + epsilon)
        
        # 9. NDMI - Normalized Difference Moisture Index
        indices['NDMI'] = (nir - swir1) / (nir + swir1 + epsilon)
        
        # 10. NBR - Normalized Burn Ratio
        indices['NBR'] = (nir - swir1) / (nir + swir1 + epsilon)
        
        return indices
    
    def calculate_statistics(self, indices, metadata):
        """Calculate comprehensive statistics for vegetation indices"""
        location_name = metadata['name']
        stats = {
            'location': location_name,
            'state': location_name.split('_')[0],
            'city': location_name.split('_')[1],
            'crop_type': metadata['crop_type'],
            'bbox': metadata['bbox'],
            'timestamp': datetime.now().isoformat()
        }
        
        for name, index in indices.items():
            # Remove invalid values
            valid_data = index[np.isfinite(index)]
            
            if len(valid_data) > 0:
                stats[f'{name}_mean'] = float(np.mean(valid_data))
                stats[f'{name}_std'] = float(np.std(valid_data))
                stats[f'{name}_min'] = float(np.min(valid_data))
                stats[f'{name}_max'] = float(np.max(valid_data))
                stats[f'{name}_median'] = float(np.median(valid_data))
                stats[f'{name}_q25'] = float(np.percentile(valid_data, 25))
                stats[f'{name}_q75'] = float(np.percentile(valid_data, 75))
                stats[f'{name}_coverage'] = float(len(valid_data) / index.size)
            else:
                # No valid data
                for stat_type in ['mean', 'std', 'min', 'max', 'median', 'q25', 'q75']:
                    stats[f'{name}_{stat_type}'] = 0.0
                stats[f'{name}_coverage'] = 0.0
        
        return stats
    
    def analyze_crop_health(self, stats):
        """Analyze crop health based on vegetation indices"""
        analysis = {
            'overall_health': 'Unknown',
            'vigor_level': 'Unknown', 
            'stress_indicators': [],
            'recommendations': [],
            'health_score': 0.0
        }
        
        ndvi = stats.get('NDVI_mean', 0)
        evi = stats.get('EVI_mean', 0) 
        savi = stats.get('SAVI_mean', 0)
        ndmi = stats.get('NDMI_mean', 0)
        lai = stats.get('LAI_mean', 0)
        
        # Health classification based on NDVI
        if ndvi > 0.6:
            analysis['overall_health'] = 'Excellent'
            analysis['vigor_level'] = 'High'
            analysis['health_score'] = 0.9
        elif ndvi > 0.4:
            analysis['overall_health'] = 'Good' 
            analysis['vigor_level'] = 'Moderate-High'
            analysis['health_score'] = 0.7
        elif ndvi > 0.2:
            analysis['overall_health'] = 'Fair'
            analysis['vigor_level'] = 'Moderate'
            analysis['health_score'] = 0.5
        elif ndvi > 0.1:
            analysis['overall_health'] = 'Poor'
            analysis['vigor_level'] = 'Low'
            analysis['health_score'] = 0.3
        else:
            analysis['overall_health'] = 'Very Poor'
            analysis['vigor_level'] = 'Very Low'
            analysis['health_score'] = 0.1
        
        # Stress indicators
        if ndvi < 0.3:
            analysis['stress_indicators'].append('Low vegetation vigor')
        if ndmi < 0.1:
            analysis['stress_indicators'].append('Water stress detected')
        if evi < 0.2:
            analysis['stress_indicators'].append('Low chlorophyll content')
        if lai < 1.0:
            analysis['stress_indicators'].append('Low leaf density')
        
        # Recommendations
        if 'Water stress detected' in analysis['stress_indicators']:
            analysis['recommendations'].append('Increase irrigation frequency')
        if 'Low vegetation vigor' in analysis['stress_indicators']:
            analysis['recommendations'].append('Consider fertilizer application')
        if 'Low chlorophyll content' in analysis['stress_indicators']:
            analysis['recommendations'].append('Monitor for nutrient deficiency')
        if len(analysis['stress_indicators']) == 0:
            analysis['recommendations'].append('Continue current management practices')
            
        return analysis
    
    def create_visualization(self, indices, metadata, stats):
        """Create comprehensive visualization of vegetation indices"""
        fig, axes = plt.subplots(2, 5, figsize=(20, 8))
        fig.suptitle(f"Agricultural Analysis: {metadata['name']} ({metadata['crop_type']})", fontsize=16)
        
        # Plot indices
        index_names = ['NDVI', 'EVI', 'SAVI', 'GNDVI', 'LAI', 'NDWI', 'NDMI', 'NBR', 'OSAVI', 'CIG']
        
        for i, name in enumerate(index_names):
            row = i // 5
            col = i % 5
            
            if name in indices:
                im = axes[row, col].imshow(indices[name], cmap='RdYlGn', vmin=-1, vmax=1)
                axes[row, col].set_title(f'{name}\nMean: {stats[f"{name}_mean"]:.3f}')
                plt.colorbar(im, ax=axes[row, col], fraction=0.046)
            else:
                axes[row, col].text(0.5, 0.5, f'{name}\nNot Available', 
                                  ha='center', va='center', transform=axes[row, col].transAxes)
            
            axes[row, col].axis('off')
        
        plt.tight_layout()
        
        # Save visualization
        viz_path = self.output_dir / "visualizations" / f"{metadata['name']}_analysis.png"
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(viz_path)
    
    def process_location(self, location_name):
        """Process a single location comprehensively"""
        print(f"🔄 Processing: {location_name}")
        
        try:
            # Load data
            img, metadata = self.load_multispectral_image(location_name)
            
            # Calculate vegetation indices
            indices = self.calculate_vegetation_indices(img)
            
            # Calculate statistics
            stats = self.calculate_statistics(indices, metadata)
            
            # Analyze crop health
            health_analysis = self.analyze_crop_health(stats)
            
            # Create visualization
            viz_path = self.create_visualization(indices, metadata, stats)
            
            # Save vegetation indices
            indices_dir = self.output_dir / "vegetation_indices" / location_name
            indices_dir.mkdir(exist_ok=True)
            
            for name, index in indices.items():
                np.save(indices_dir / f"{name}.npy", index)
            
            # Save comprehensive analysis
            analysis = {
                'statistics': stats,
                'health_analysis': health_analysis,
                'visualization_path': viz_path,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            analysis_path = self.output_dir / "analysis_reports" / f"{location_name}_analysis.json"
            with open(analysis_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print(f"✅ {location_name}: Health={health_analysis['overall_health']}, NDVI={stats['NDVI_mean']:.3f}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error processing {location_name}: {e}")
            return None
    
    def process_all_locations(self):
        """Process all available locations"""
        print("\n🚀 AGROVISION AI: COMPREHENSIVE MULTISPECTRAL PROCESSING")
        print("=" * 60)
        
        # Find all locations
        locations = []
        for file in self.data_dir.glob("*_multispectral.npy"):
            location = file.stem.replace('_multispectral', '')
            locations.append(location)
        
        print(f"📊 Found {len(locations)} locations to process")
        
        all_analyses = []
        successful = 0
        
        for location in sorted(locations):
            analysis = self.process_location(location)
            if analysis:
                all_analyses.append(analysis)
                successful += 1
        
        print(f"\n✅ Successfully processed: {successful}/{len(locations)} locations")
        
        # Create comprehensive summary
        self.create_comprehensive_summary(all_analyses)
        
        return all_analyses
    
    def create_comprehensive_summary(self, all_analyses):
        """Create comprehensive agricultural summary"""
        print("\n📊 Creating comprehensive agricultural summary...")
        
        # Aggregate statistics
        summary_stats = []
        
        for analysis in all_analyses:
            stats = analysis['statistics']
            health = analysis['health_analysis']
            
            summary_stats.append({
                'location': stats['location'],
                'state': stats['state'],
                'city': stats['city'],
                'crop_type': stats['crop_type'],
                'ndvi_mean': stats['NDVI_mean'],
                'evi_mean': stats['EVI_mean'],
                'savi_mean': stats['SAVI_mean'],
                'lai_mean': stats['LAI_mean'],
                'health_score': health['health_score'],
                'overall_health': health['overall_health'],
                'vigor_level': health['vigor_level'],
                'stress_count': len(health['stress_indicators'])
            })
        
        df = pd.DataFrame(summary_stats)
        
        # Save detailed CSV
        csv_path = self.output_dir / "statistics" / "comprehensive_agricultural_analysis.csv"
        df.to_csv(csv_path, index=False)
        
        # Create summary report
        summary = {
            'processing_summary': {
                'total_locations': len(all_analyses),
                'processing_date': datetime.now().isoformat(),
                'geographic_coverage': {
                    'states': sorted(df['state'].unique().tolist()),
                    'total_states': df['state'].nunique(),
                    'total_cities': df['city'].nunique()
                }
            },
            'agricultural_insights': {
                'crop_types': df['crop_type'].value_counts().to_dict(),
                'health_distribution': df['overall_health'].value_counts().to_dict(),
                'average_ndvi_by_state': df.groupby('state')['ndvi_mean'].mean().to_dict(),
                'average_health_score_by_crop': df.groupby('crop_type')['health_score'].mean().to_dict()
            },
            'top_performing_regions': {
                'highest_ndvi': df.nlargest(5, 'ndvi_mean')[['location', 'ndvi_mean', 'overall_health']].to_dict('records'),
                'highest_health_score': df.nlargest(5, 'health_score')[['location', 'health_score', 'overall_health']].to_dict('records')
            },
            'areas_needing_attention': {
                'lowest_ndvi': df.nsmallest(5, 'ndvi_mean')[['location', 'ndvi_mean', 'overall_health']].to_dict('records'),
                'highest_stress': df.nlargest(5, 'stress_count')[['location', 'stress_count', 'overall_health']].to_dict('records')
            },
            'recommendations': {
                'immediate_attention': df[df['health_score'] < 0.4]['location'].tolist(),
                'monitor_closely': df[(df['health_score'] >= 0.4) & (df['health_score'] < 0.6)]['location'].tolist(),
                'excellent_performance': df[df['health_score'] >= 0.8]['location'].tolist()
            }
        }
        
        # Save summary report
        summary_path = self.output_dir / "AGROVISION_COMPREHENSIVE_REPORT.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print key insights
        print("\n🌾 AGRICULTURAL INSIGHTS SUMMARY")
        print("=" * 40)
        print(f"📍 Total Locations Analyzed: {len(all_analyses)}")
        print(f"🗺️ States Covered: {df['state'].nunique()}")
        print(f"🌱 Crop Types: {', '.join(df['crop_type'].unique())}")
        print(f"📊 Average NDVI: {df['ndvi_mean'].mean():.3f}")
        print(f"🏆 Best Performing: {df.loc[df['ndvi_mean'].idxmax(), 'location']} (NDVI: {df['ndvi_mean'].max():.3f})")
        print(f"⚠️ Needs Attention: {df.loc[df['ndvi_mean'].idxmin(), 'location']} (NDVI: {df['ndvi_mean'].min():.3f})")
        
        print(f"\n📁 Comprehensive report saved: {summary_path}")
        print(f"📊 Detailed data saved: {csv_path}")
        
        return summary

def main():
    """Main processing pipeline"""
    print("🌾 AgroVision AI - Advanced Multispectral Processing Pipeline")
    print("=" * 60)
    
    # Initialize processor
    processor = AgroVisionPreprocessor()
    
    # Process all locations
    results = processor.process_all_locations()
    
    print("\n🎉 PROCESSING COMPLETE!")
    print(f"✅ Generated comprehensive agricultural analysis for {len(results)} locations")
    print("📂 Check 'processed_agrovision' folder for all outputs")
    print("🚀 Ready for AgroVision AI model training!")

if __name__ == "__main__":
    main()