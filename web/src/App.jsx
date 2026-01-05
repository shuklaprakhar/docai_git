import React from 'react'
import UploadForm from './components/UploadForm'

export default function App() {
  return (
    <div className="app">
      <header>
        <h1>Referral Agent — Ingest & Scrub</h1>
      </header>
      <main>
        <UploadForm />
      </main>
    </div>
  )
}
