import '../styles/globals.css'
import { useEffect, useState } from 'react'

function MyApp({ Component, pageProps }) {
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Check if user is logged in (has token)
    const token = localStorage.getItem('token')
    if (token) {
      setUser(JSON.parse(localStorage.getItem('user')))
    }
  }, [])

  return <Component {...pageProps} user={user} setUser={setUser} />
}

export default MyApp