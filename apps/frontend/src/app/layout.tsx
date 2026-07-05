import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'StudyMateAI - Academic AI Mentor',
  description: 'Your curriculum-aligned study companion for Physics and Chemistry preparation.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  )
}
