# 📋 Form Pipeline

Automated student form submission pipeline with spreadsheet cleaning and validation.

## 🌐 Overview

This web application allows users to upload student spreadsheets and automatically fill out and submit forms using browser automation. The system cleans and validates data, then uses Playwright (running on Google Cloud Run) to submit each student's information.

### Architecture

- **Frontend**: Next.js deployed on Vercel
- **Backend**: FastAPI + Playwright deployed on Google Cloud Run
- **Runtime**: All browser automation happens in the cloud (not locally)

## 🚀 Features

### Tab 1 - Clean Spreadsheet
- Upload Excel files with student data
- Automatic data cleaning and validation
- Smart fixes for common formatting issues
- Display unfixable rows directly on screen
- Download cleaned spreadsheet
- Duplicate detection

### Tab 2 - Submit Forms
- Automated form filling with Playwright
- Real-time progress tracking (progress bar, counter, timer)
- Live log with color-coded results
- Pause/Resume/Kill controls
- Final summary with failed rows table

## 📄 Data Cleaning Rules

### Supported Fixes
- **Phone Numbers**: `(636) 480-1423` → `6364801423`
- **ZIP Codes**: `60163-1234` → `60163`
- **Dates of Birth**: `3/7/2007` → `03/07/2007`
- **Future Year DOB**: Auto-corrected to age 16

### Validation Rules
- **Names**: Letters, spaces, hyphens, apostrophes only
- **Email**: Standard email format
- **Phone**: 10 digits after cleaning
- **ZIP**: 5 digits after cleaning
- **DOB**: Between 1950 and current year

## 📁 Repository Structure

```
form-pipeline/
├── frontend/          # Next.js app (Vercel)
│   ├── app/          # Next.js 14 app directory
│   ├── components/   # React components (to be added)
│   └── README.md     # Frontend setup guide
├── backend/          # FastAPI app (Cloud Run)
│   ├── main.py       # FastAPI application
│   ├── Dockerfile    # Container configuration
│   └── README.md     # Backend setup guide
└── README.md         # This file
```

## 🛠️ Local Development

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at [http://localhost:3000](http://localhost:3000)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload
```

Backend runs at [http://localhost:8000](http://localhost:8000)

See individual README files in `/frontend` and `/backend` for detailed setup instructions.

## 🚀 Deployment

### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Set environment variable: `NEXT_PUBLIC_API_URL`
3. Deploy automatically on push

### Backend (Google Cloud Run)
1. Build container: `gcloud builds submit`
2. Deploy: `gcloud run deploy form-pipeline-backend`
3. Configure memory (2Gi) and timeout (3600s)

See individual README files for detailed deployment steps.

## 🔧 Environment Variables

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL

### Backend
- `ENV`: Environment (development/production)
- `PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins

## 📝 Required Spreadsheet Format

Excel file must have these exact headers:

```
Email Address | First Name | Last Name | Phone | Date of Birth | Zip Code
```

Example:
```
bsavila03@gmail.com | Brithany | Avila | 7088828259 | 3/16/2007 | 60163
```

## 🎯 Target Form

Currently configured for: https://www.goarmy.com/info?iom=CKXG-XX_LAP_Exhibit_2897052_C04_NA_ROTC

All target URLs must share the same HTML structure.

## 📊 Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Axios

### Backend
- FastAPI
- Playwright
- Pandas & OpenPyXL
- Uvicorn

## 📄 License

Private project - All rights reserved

## 🤝 Contributing

This is a private project. Contact the repository owner for contribution guidelines.

