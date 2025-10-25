export interface Farm {
  id: string;
  user_id: string;
  name: string;
  crop_type: string;
  latitude: number;
  longitude: number;
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
  metadata?: any;
}

export interface ChatMessage {
  id: string;
  user_id: string;
  farm_id?: string;
  message: string;
  response_text: string;
  suggestions?: string[];
  intent: string;
  entities?: any;
  confidence?: string;
  timestamp: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  created_at: string;
}
