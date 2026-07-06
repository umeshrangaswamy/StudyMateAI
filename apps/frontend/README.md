# StudyMateAI Frontend Application

This is the static frontend client for **StudyMateAI (MVP)**. It is built using **Next.js**, **TypeScript**, and **Tailwind CSS**, designed for compilation to static assets deployed directly onto **Firebase Hosting**.

## 🎨 Visual Design & UX Features

- **Typography:** Uses modern Google Font families (e.g. Outfit and Inter) rather than generic browser fallbacks.
- **Styling:** Custom-tailored dark and light palettes leveraging semantic CSS variables.
- **Layout:** Fully responsive multi-panel workspace supporting:
  - Concept explanation & doubt resolution.
  - Interactive multiple choice question (MCQ) testing with custom feedback loops.
  - Grade reports and teacher evaluation tracking.
  - Student learning profile and revision tips indicators.

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

Because our architecture utilizes serverless hosting with no Node.js server overhead, we compile the app to static HTML, CSS, and JS assets:

```bash
# Build & export application
npm run build
```

This compiles files directly into the **`apps/frontend/out/`** directory.

The Firebase configuration (`firebase.json` at the root directory) points its `public` directory target directly to `apps/frontend/out`.
