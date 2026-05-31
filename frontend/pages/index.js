import { useState } from 'react'
import { useRouter } from 'next/router'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function Home() {
  const router = useRouter()
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      let response
      
      if (isLogin) {
        // LOGIN
        response = await axios.post(`${API_URL}/api/login`, {
          email,
          password
        })
      } else {
        // REGISTER
        response = await axios.post(`${API_URL}/api/register`, {
          email,
          full_name: fullName,
          password
        })
      }

      // Save token and user data
      const { access_token, user_id } = response.data
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify({ email, user_id }))

      // Redirect to dashboard
      router.push('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>SmartHub</h1>
        <h2>{isLogin ? 'Login' : 'Register'}</h2>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <input
              type="text"
              placeholder="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          )}

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit" disabled={loading}>
            {loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}
          </button>
        </form>

        <p>
          {isLogin ? "Don't have an account? " : 'Already have an account? '}
          <button 
            type="button" 
            onClick={() => {
              setIsLogin(!isLogin)
              setError('')
            }}
            className="toggle-btn"
          >
            {isLogin ? 'Register' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  )
}