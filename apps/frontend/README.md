# StudyMateAI Frontend Application

This is the static frontend client for **StudyMateAI (Free Tier)**. It is built using **Next.js**, **TypeScript**, and **Tailwind CSS**, designed for compilation to static assets deployed directly onto **Firebase Hosting**.

## 🚀 Running Locally

### 1. Prerequisites
- Node.js (v18+) and npm installed

### 2. Installation
```bash
# Navigate to the frontend directory
cd apps/frontend

# Install dependencies
npm install
```

### 3. Run Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

## 📦 Building static output for Firebase Hosting

Because our architecture utilizes serverless hosting with no Next.js Node.js server overhead, we compile the app to static HTML, CSS, and JS assets:

```bash
# Build & export application
npm run build
```

This compiles files directly into a new **`apps/frontend/out/`** directory.

To configure Firebase Hosting to read this static directory, point the `public` directory key in your `firebase.json` configuration file to `apps/frontend/out`.
