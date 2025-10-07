# Form Pipeline Frontend

Next.js frontend for the Form Pipeline application.

## Features

- Upload and validate student spreadsheets
- Clean and fix data automatically
- Submit forms via automated backend
- Real-time progress tracking

## Local Development

### Prerequisites

- Node.js 18+ and npm

### Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
cp .env.example .env.local
```

3. Update the API URL in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## Production Build

```bash
npm run build
npm start
```

## Deployment to Vercel

### Quick Deploy

1. Push code to GitHub
2. Import repository in Vercel
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Cloud Run backend URL

### Manual Deploy

```bash
npm install -g vercel
vercel
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (required)

## Tech Stack

- Next.js 14
- TypeScript
- Tailwind CSS
- Axios for API calls

