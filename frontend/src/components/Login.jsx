import { useState } from 'react'
import axios from 'axios'

function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    if (!email || !password) {
      setError('Please enter both email and password')
      setLoading(false)
      return
    }

    try {
      const emailToUse = email.trim().toLowerCase()
      const res = await axios.post('/auth/token', new URLSearchParams({
        username: emailToUse,
        password: password
      }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      if (res.data && res.data.access_token) {
        localStorage.setItem('token', res.data.access_token)
        onLogin()
      } else {
        setError('Login failed: Invalid server response')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message
      setError('Login failed: ' + errorMsg)
    }
    setLoading(false)
  }

  return (
    <div className="auth-form">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default Login