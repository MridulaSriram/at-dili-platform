
import { useState } from 'react'

const API_URL = 'https://at-dili-backend.onrender.com'

const initialValues = {
  nat2_slow: '0',
  cyp2e1_c1c1: '0',
  gstm1_null: '0',
  gstt1_null: '0',
  age: '35',
  female: '0',
  alcohol: '0',
  hiv: '0',
  albumin: '3.8',
  bmi: '21.5',
}

// Moved outside Dashboard to prevent focus loss
function SelectField({ label, name, options, value, onChange }) {
  return (
    <div className="demo-field">
      <label htmlFor={name}>{label}</label>
      <select
        id={name}
        name={name}
        value={value}
        onChange={onChange}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}

// Moved outside Dashboard to prevent focus loss
function NumberField({
  label,
  name,
  min,
  max,
  step = '1',
  value,
  onChange,
}) {
  return (
    <div className="demo-field">
      <label htmlFor={name}>{label}</label>
      <input
        id={name}
        name={name}
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={onChange}
        required
      />
    </div>
  )
}

function Dashboard() {
  const [values, setValues] = useState(initialValues)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const updateValue = (event) => {
    const { name, value } = event.target

    setValues((previous) => ({
      ...previous,
      [name]: value,
    }))

    setResult(null)
    setError('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    setLoading(true)
    setResult(null)
    setError('')

    try {
      const payload = {
        nat2_slow: Number(values.nat2_slow),
        cyp2e1_c1c1: Number(values.cyp2e1_c1c1),
        gstm1_null: Number(values.gstm1_null),
        gstt1_null: Number(values.gstt1_null),
        age: Number(values.age),
        female: Number(values.female),
        alcohol: Number(values.alcohol),
        hiv: Number(values.hiv),
        albumin: Number(values.albumin),
        bmi: Number(values.bmi),
      }

      const response = await fetch(`${API_URL}/demo/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to generate the demonstration output.'
        )
      }

      setResult(data)
    } catch (err) {
      setError(
        err.message === 'Failed to fetch'
          ? 'Unable to connect to the demonstration API. The free server may be starting up. Please try again shortly.'
          : err.message
      )
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setValues(initialValues)
    setResult(null)
    setError('')
  }

  return (
    <>
      {/* Hero section */}
      <section className="hero">
        <div className="hero-content">
          <span className="eyebrow">
            GENETICS • PHARMACOGENOMICS • RESEARCH
          </span>

          <h1>
            Understanding genetic risk in <span>AT-DILI</span>
          </h1>

          <p>
            Explore how genetic variation may contribute to
            anti-tubercular drug-induced liver injury. This academic
            project demonstrates a research workflow using a
            synthetic-data model.
          </p>

          <a href="#dashboard" className="primary-button">
            Explore Prediction Dashboard <span>→</span>
          </a>
        </div>

        <div className="hero-visual">
          <div className="orbit"></div>
          <div className="orbit orbit-two"></div>

          <div className="science-card">
            <div className="science-icon">⌬</div>
            <span>RESEARCH PROJECT</span>
            <div className="science-line"></div>
            <strong>AT-DILI Analysis</strong>
            <small>Genetic research platform</small>
            <div className="science-line"></div>
            <small>Synthetic demo model connected</small>
          </div>

          <div className="floating-chip chip-top">
            GENETIC RESEARCH
          </div>

          <div className="floating-chip chip-bottom">
            SYNTHETIC DEMONSTRATION
          </div>
        </div>
      </section>

      {/* Prediction dashboard */}
      <section className="dashboard-section" id="dashboard">
        <div className="section-heading">
          <div>
            <span className="eyebrow">PREDICTION WORKSPACE</span>
            <h2>AT-DILI Prediction Dashboard</h2>
          </div>

          <div className="status-pill">
            <span className="status-dot"></span>
            Demo model connected
          </div>
        </div>

        <div className="notice">
          <div className="notice-icon">i</div>
          <p>
            <strong>Educational demonstration only:</strong> This
            model was trained entirely on synthetic data. The
            outputs are simulated examples, not medical risk
            estimates. Do not enter real patient information or use
            the results for clinical decisions.
          </p>
        </div>

        <form className="dashboard-card demo-form" onSubmit={handleSubmit}>
          <div className="card-symbol">⌬</div>

          <h3>Genetic and Clinical Demonstration Inputs</h3>

          <p>
            Enter fictional illustrative values to explore how the
            demonstration model responds.
          </p>

          <div className="demo-input-section">
            <h4>Genetic demonstration inputs</h4>

            <div className="demo-grid">
              <SelectField
                label="NAT2 slow acetylator feature"
                name="nat2_slow"
                value={values.nat2_slow}
                onChange={updateValue}
                options={[
                  { value: '0', label: 'No' },
                  { value: '1', label: 'Yes' },
                ]}
              />

              <SelectField
                label="CYP2E1 c1/c1 feature"
                name="cyp2e1_c1c1"
                value={values.cyp2e1_c1c1}
                onChange={updateValue}
                options={[
                  { value: '0', label: 'No' },
                  { value: '1', label: 'Yes' },
                ]}
              />

              <SelectField
                label="GSTM1 null feature"
                name="gstm1_null"
                value={values.gstm1_null}
                onChange={updateValue}
                options={[
                  { value: '0', label: 'Present' },
                  { value: '1', label: 'Null' },
                ]}
              />

              <SelectField
                label="GSTT1 null feature"
                name="gstt1_null"
                value={values.gstt1_null}
                onChange={updateValue}
                options={[
                  { value: '0', label: 'Present' },
                  { value: '1', label: 'Null' },
                ]}
              />
            </div>
          </div>

          <div className="demo-input-section">
            <h4>Clinical demonstration inputs</h4>

            <div className="demo-grid">
              <NumberField
                label="Age (years)"
                name="age"
                min="15"
                max="80"
                value={values.age}
                onChange={updateValue}
              />

              <SelectField
                label="Gender"
                name="female"
                value={values.female}
                onChange={updateValue}
                options={[
                  { value: '1', label: 'Female' },
                  { value: '0', label: 'Male' },
                ]}
              />

              <SelectField
                label="Alcoholic"
                name="alcohol"
                value={values.alcohol}
                onChange={updateValue}
                options={[
                  { value: '1', label: 'Yes' },
                  { value: '0', label: 'No' },
                ]}
              />

              <SelectField
                label="HIV Presence"
                name="hiv"
                value={values.hiv}
                onChange={updateValue}
                options={[
                  { value: '1', label: 'HIV Positive' },
                  { value: '0', label: 'HIV Negative' },
                ]}
              />

              <NumberField
                label="Albumin (g/dL)"
                name="albumin"
                min="1.8"
                max="5.0"
                step="0.1"
                value={values.albumin}
                onChange={updateValue}
              />

              <NumberField
                label="BMI (kg/m²)"
                name="bmi"
                min="12"
                max="35"
                step="0.1"
                value={values.bmi}
                onChange={updateValue}
              />
            </div>
          </div>

          <div className="demo-actions">
            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Demo Output'}
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={handleReset}
              disabled={loading}
            >
              Reset Inputs
            </button>
          </div>

          {error && (
            <div className="demo-error" role="alert">
              {error}
            </div>
          )}

          {result && (
            <div className="demo-result" aria-live="polite">
              <span className="eyebrow">SYNTHETIC DEMO OUTPUT</span>

              <h3>Illustrative Model Probability</h3>

              <div className="demo-probability">
                {result.percentage.toFixed(2)}%
              </div>

              <p>
                This is a simulated output from the Combined (L2)
                demonstration model.
              </p>

              <div className="demo-result-details">
                <span>Model: {result.model_name}</span>
                <span>Clinical validation: No</span>
                <span>Demo output: Yes</span>
              </div>

              <div className="notice demo-disclaimer">
                <div className="notice-icon">i</div>
                <p>{result.disclaimer}</p>
              </div>
            </div>
          )}

          <small className="demo-footer-note">
            Synthetic educational prototype · Not for diagnosis,
            treatment decisions or real patient assessment.
          </small>
        </form>
      </section>
    </>
  )
}

export default Dashboard
