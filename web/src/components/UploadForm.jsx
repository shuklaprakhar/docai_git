import React, { useState } from 'react'
import axios from 'axios'

export default function UploadForm() {
  const [files, setFiles] = useState(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  const onChange = (e) => setFiles(e.target.files)

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!files || files.length === 0) return
    setLoading(true)
    const fd = new FormData()
    for (let i = 0; i < files.length; i++) fd.append('files', files[i])
    try {
      const resp = await axios.post('http://127.0.0.1:8001/ingest', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResults(resp.data)
    } catch (err) {
      console.error(err)
      alert('Failed to upload — check the backend server')
    } finally {
      setLoading(false)
    }
  }

  const onApprove = (idx) => {
    // Placeholder for approve action — in a real app this would call an approval API
    alert(`Approved result ${idx}`)
  }

  return (
    <div className="upload-form">
      <form onSubmit={onSubmit}>
        <label>
          Select referral PDF(s):
          <input type="file" accept="application/pdf" multiple onChange={onChange} />
        </label>
        <div>
          <button type="submit" disabled={loading}>{loading ? 'Scrubbing…' : 'Scrub information'}</button>
        </div>
      </form>

      {results && (
        <div className="results">
          <h2>Results</h2>
          {results.results.map((r, i) => (
            <div key={i} className="result">
              <h3>{r.file}</h3>
              <pre>{JSON.stringify(r.extracted, null, 2)}</pre>
              <button onClick={() => onApprove(i)}>Approve</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
