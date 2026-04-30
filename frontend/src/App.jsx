import { useState, useEffect } from 'react'
import axios from 'axios'
import Login from './components/Login'
import Register from './components/Register'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || (['localhost', '127.0.0.1'].includes(window.location.hostname) ? 'http://localhost:8000' : '/api')
axios.defaults.baseURL = API_BASE_URL

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      axios.get('/auth/verify')
        .then(() => setIsAuthenticated(true))
        .catch(() => {
          localStorage.removeItem('token')
          delete axios.defaults.headers.common['Authorization']
        })
    }
  }, [])

  const handleLogin = () => {
    setIsAuthenticated(true)
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    setIsAuthenticated(false)
    setResponse('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) {
      setResponse('Error: Please enter a question or description')
      return
    }
    setLoading(true)
    setResponse('')
    try {
      const res = await axios.post('/agent/plan', { query })
      if (res.data && res.data.response) {
        setResponse(res.data.response)
        setQuery('')
      } else {
        setResponse('Error: No response from server')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message
      setResponse('Error: ' + errorMsg)
      console.error('Agent error:', error)
    }
    setLoading(false)
  }

  return (
    <div className="App">
      <div className="page-shell">
        <div className="brand-bar">
          <div>
            <p className="eyebrow">Smart Travel Planner</p>
            <h1>Your next unforgettable trip is one question away</h1>
          </div>
          {isAuthenticated && (
            <button className="secondary" onClick={handleLogout}>
              Logout
            </button>
          )}
        </div>

        {!isAuthenticated ? (
          <div className="auth-shell">
            <div className="hero-card">
              <h2>Ready to explore smarter?</h2>
              <p>
                Use AI-powered planning to discover destinations that match your style,
                budget, and mood. Sign in or create an account to get started.
              </p>
            </div>
            <div className="auth-card">
              {showRegister ? (
                <Register onRegister={() => setShowRegister(false)} />
              ) : (
                <Login onLogin={handleLogin} />
              )}
              <div className="form-footer">
                <span>
                  {showRegister ? 'Already have an account?' : "Don't have an account?"}
                </span>
                <button className="link-button" onClick={() => setShowRegister(!showRegister)}>
                  {showRegister ? 'Login' : 'Register'}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="planner-card">
            <div className="planner-intro">
              <h2>Describe your dream getaway</h2>
              <p>
                Tell us the destination type, budget, travel dates, and any special preferences.
              </p>
            </div>
            <form onSubmit={handleSubmit}>
              <textarea
                className="trip-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Example: Two-week beach vacation in Spain for under $2500 with a focus on food and culture."
                rows={5}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Planning...' : 'Plan Trip'}
              </button>
            </form>
            {response && (
              <div className="response-card">
                <div className="response-header">
                  <h2>Trip Plan</h2>
                  <span>Personalized travel ideas based on your request</span>
                </div>
                <p>{response}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
