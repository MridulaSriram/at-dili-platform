
import './App.css'
import Dashboard from './pages/Dashboard'
import About from './pages/About'

function App() {
  return (
    <div className="app">
      <header className="navbar">
        <a className="brand" href="#dashboard">
          <span className="brand-icon">A</span>
          <span>
            <strong>AT-DILI</strong>
            <small>Research &amp; Prediction Platform</small>
          </span>
        </a>

        <nav>
          <a href="#dashboard">Dashboard</a>
          <a href="#about">About AT-DILI</a>
        </nav>
      </header>

      <main>
        <Dashboard />
        <About />
      </main>

      <footer className="footer">
        <a className="footer-brand" href="#dashboard">
          AT-DILI Research Platform
        </a>
        <span>Academic biotechnology project · Prototype</span>
      </footer>
    </div>
  )
}

export default App
