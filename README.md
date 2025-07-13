# GymformAI - AI-Powered Fitness Form Analysis

A production-grade micro-SaaS application that analyzes workout videos using computer vision and AI to provide real-time form feedback, rep counting, and personalized corrections.

## Features

- **Video Analysis**: Upload or capture workout videos (max 20MB)
- **AI Form Assessment**: Get detailed form scores (1-10) with posture analysis
- **Rep Counting**: Automatic repetition counting from video analysis
- **Risk Detection**: Identify 2 main posture issues per exercise
- **Personalized Corrections**: Get specific improvement recommendations
- **Authentication**: Supabase Auth with email and Google OAuth
- **Subscription Plans**: Free (3 analyses/day) and Pro (€9.99/month unlimited)
- **Analytics**: Track user engagement and subscription metrics

## Tech Stack

### Frontend
- **Next.js 14** with TypeScript
- **TailwindCSS** for styling
- **React Hook Form** for form handling
- **Axios** for API calls
- **React Dropzone** for file uploads

### Backend
- **FastAPI** with Python 3.11+
- **OpenCV** for video processing
- **MediaPipe** for pose estimation
- **OpenAI GPT-4 Turbo** for form analysis
- **Pydantic** for data validation

### Infrastructure
- **Supabase** for authentication and database
- **Stripe** for payment processing
- **Docker** for containerization
- **Mixpanel** for analytics

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ and Python 3.11+
- OpenAI API key
- Supabase project
- Stripe account

### Local Development

1. **Clone and setup environment**:
```bash
git clone <repository-url>
cd GymformAI
cp .env.example .env
# Edit .env with your API keys
```

2. **Start with Docker Compose**:
```bash
docker-compose up -d
```

3. **Or run locally**:
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Stripe
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
STRIPE_PRICE_ID=your_stripe_price_id

# Analytics
MIXPANEL_TOKEN=your_mixpanel_token

# App Config
MAX_FILE_SIZE=20971520
ALLOWED_VIDEO_TYPES=mp4,webm,mov
```

## API Endpoints

### POST /api/analyze
Analyze workout video and return form assessment.

**Request**: Multipart form data with video file
**Response**: JSON with exercise analysis

```json
{
  "exercise": "squat",
  "score": 7.5,
  "risks": ["Knees caving inward", "Not reaching parallel"],
  "corrections": ["Keep knees aligned with toes", "Lower until thighs are parallel to ground"],
  "rep_count": 12
}
```

## Database Schema

### users
- id (uuid, primary key)
- email (text, unique)
- subscription_status (text)
- subscription_id (text)
- created_at (timestamp)

### analyses
- id (uuid, primary key)
- user_id (uuid, foreign key)
- video_filename (text)
- exercise_type (text)
- form_score (numeric)
- rep_count (integer)
- risks (jsonb)
- corrections (jsonb)
- keypoints_data (jsonb)
- created_at (timestamp)

## Deployment

### Production Setup

1. **Deploy Backend**:
```bash
cd backend
docker build -t gymformai-backend .
docker run -p 8000:8000 --env-file .env gymformai-backend
```

2. **Deploy Frontend**:
```bash
cd frontend
npm run build
docker build -t gymformai-frontend .
docker run -p 3000:3000 gymformai-frontend
```

3. **Configure Reverse Proxy** (Nginx example):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

## Security Considerations

- File upload validation and sanitization
- Rate limiting on API endpoints
- CORS configuration
- Environment variable protection
- Input validation with Pydantic
- Secure file storage and cleanup

## Performance Optimizations

- Video frame extraction optimization
- Pose estimation model caching
- Database query optimization
- CDN for static assets
- Image compression for analysis results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support, email support@gymformai.com or create an issue in the repository. 