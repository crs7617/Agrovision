export interface Farm {
  id: string;
  user_id: string;
  name: string;
  crop_type: string;
  lat: number;
  lng: number;
  area: number;
  created_at: string;
  updated_at: string;
}

export interface Analysis {
  id: string;
  farm_id: string;
  timestamp: string;
  ndvi: number;
  evi: number;
  savi: number;
  health_score: number;
  satellite_image_url?: string;
  metadata?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  user_id: string;
  farm_id?: string;
  message: string;
  response_text: string;
  suggestions?: string[];
  intent: string;
  entities?: Record<string, unknown>;
  confidence?: string;
  timestamp: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  user_metadata?: {
    name?: string;
    avatar_url?: string;
  };
  created_at: string;
}

export interface CreateFarmData {
  name: string;
  crop_type: string;
  latitude: string;
  longitude: string;
  area: string;
  description?: string;
}

export interface HealthZone {
  zone_id: number;
  ndvi_range: [number, number];
  area_percentage: number;
  health_status: 'excellent' | 'good' | 'moderate' | 'poor';
  recommendations: string[];
}

export interface WeatherData {
  date: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  wind_speed: number;
}

