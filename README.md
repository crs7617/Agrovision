# AgroVision

A precision agriculture platform leveraging satellite imagery and AI to provide real-time crop health monitoring, intelligent diagnostics, and actionable farming insights.

## Features

- **Satellite Analysis**: Automated processing of multispectral satellite imagery with NDVI, EVI, and SAVI vegetation indices
- **Health Monitoring**: Real-time crop health assessment with zone-based segmentation and anomaly detection
- **AI Assistant**: Intelligent chatbot providing crop-specific recommendations and problem diagnosis
- **Weather Integration**: Current conditions and forecasts correlated with crop health metrics
- **Farm Management**: Multi-farm dashboard with historical trend analysis and performance tracking

## Tech Stack

**Frontend**
- Next.js 16 with React 19
- TypeScript
- Tailwind CSS v4
- Supabase Auth
- React Query for state management
- Recharts for data visualization
- React Leaflet for mapping

**Backend**
- FastAPI (Python)
- Supabase (PostgreSQL)
- Google Gemini AI
- OpenWeather API
- NumPy for spectral analysis

## Setup

### Prerequisites

- Node.js 20+
- Python 3.12+
- Supabase account
- Google AI API key
- OpenWeather API key

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python main.py
```

### Frontend

```bash
cd frontend/agrovision-app
npm install
cp .env.local.example .env.local
# Add your Supabase credentials to .env.local
npm run dev
```

### Docker

```bash
docker compose up --build
```

## Environment Variables

**Backend** (`.env`)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
GOOGLE_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_key
FRONTEND_URL=http://localhost:3001
```

**Frontend** (`.env.local`)
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Database Setup

Run the SQL schema:

```bash
psql -h your_supabase_host -U postgres -d postgres -f backend/supabase_schema.sql
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## License

MIT
