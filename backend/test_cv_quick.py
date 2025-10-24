from services.cv_service import FieldDetector
import numpy as np

d = FieldDetector()
r = d.detect_field_boundaries(np.random.rand(4, 640, 640))
print(f'✅ Detection works! Found {r["num_detections"]} fields')
