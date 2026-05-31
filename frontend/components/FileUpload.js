import { useEffect, useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function FileUpload({ token }) {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [selectedFile, setSelectedFile] = useState(null)

  useEffect(() => {
    fetchFiles()
  }, [token])

  const fetchFiles = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/documents?token=${token}`
      )
      setFiles(response.data)
    } catch (err) {
      console.error('Error fetching files:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e) => {
    if (!e.target.files[0]) return
    setSelectedFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      await axios.post(
        `${API_URL}/api/documents/upload?token=${token}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      setSelectedFile(null)
      document.getElementById('file-input').value = ''

      fetchFiles()
    } catch (err) {
      console.error('Upload error:', err)
      alert('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleDownload = async (docId, filename) => {
    try {
      const response = await axios.get(
        `${API_URL}/api/documents/${docId}?token=${token}`,
        {
          responseType: 'blob'
        }
      )

      const url = window.URL.createObjectURL(response.data)

      const link = document.createElement('a')
      link.href = url
      link.download = filename

      document.body.appendChild(link)
      link.click()
      link.remove()

      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download error:', err)
    }
  }

  if (loading) {
    return <div>Loading files...</div>
  }

  return (
    <div className="upload-section">

      <div className="upload-card">

        <h3>📁 Upload Documents</h3>

        <label htmlFor="file-input" className="upload-dropzone">
          <div className="upload-icon">☁️</div>

          <p>
            {selectedFile
              ? selectedFile.name
              : 'Click to select a file'}
          </p>

          <span>
            PDF, DOCX, TXT and other files
          </span>
        </label>

        <input
          id="file-input"
          type="file"
          onChange={handleFileSelect}
          hidden
        />

        <button
          className="upload-btn"
          disabled={!selectedFile || uploading}
          onClick={handleUpload}
        >
          {uploading ? 'Uploading...' : 'Upload File'}
        </button>

      </div>

      <div className="files-list">

        <h3>Your Documents ({files.length})</h3>

        {files.length === 0 ? (
          <div className="empty-state">
            No documents uploaded yet
          </div>
        ) : (
          files.map((file) => (
            <div
              key={file.id}
              className="file-card"
            >
              <div>
                <strong>{file.filename}</strong>

                <br />

                <small>
                  {(file.file_size / 1024).toFixed(2)} KB
                </small>
              </div>

              <button
                className="download-btn"
                onClick={() =>
                  handleDownload(
                    file.id,
                    file.filename
                  )
                }
              >
                Download
              </button>
            </div>
          ))
        )}

      </div>
    </div>
  )
}