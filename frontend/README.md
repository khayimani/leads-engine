# Leads Engine Frontend

This is the frontend for the Leads Engine service, built with Next.js and Tailwind CSS. It is designed to match the aesthetic of the main NovraLab site.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment variables:
   Create a `.env.local` file with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## Deployment on Vercel

1. Connect this repository to Vercel.
2. Set the root directory to `frontend`.
3. Add the `NEXT_PUBLIC_API_URL` environment variable pointing to your deployed FastAPI backend.
4. Configure your subdomain (e.g., `leads.novralab.com`) in the Vercel dashboard.

## Aesthetic Cohesion

The project uses the following design tokens from the main site:
- Background: `#ffffff`
- Foreground: `#0b0b0b`
- Muted: `#6b7280`
- Grid Background Pattern
- Animated Logo Reveal
- Custom Button and Card styles
