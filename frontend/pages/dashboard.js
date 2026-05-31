import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'

import Navigation from '../components/Navigation'
import NotesList from '../components/NotesList'
import FileUpload from '../components/FileUpload'

export default function Dashboard() {
  const router = useRouter()

  const [token, setToken] = useState('')
  const [user, setUser] = useState(null)

  useEffect(() => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')

    if (!savedToken) {
      router.push('/')
      return
    }

    setToken(savedToken)

    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
  }, [])

  if (!token) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <Navigation user={user} />

      <div className="container">
        <h2>Dashboard</h2>

        <div className="section">
          <h3>Notes</h3>
          <NotesList token={token} />
        </div>

        <div className="section">
          <h3>Documents</h3>
          <FileUpload token={token} />
        </div>
      </div>
    </div>
  )
}