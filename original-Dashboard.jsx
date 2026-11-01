
import { useState } from 'react'

const API_URL = 'http://127.0.0.1:8000'

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

// --------------------------------------------------
// Reusable dropdown component
// --------------------------------------------------

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

// --------------------------------------------------
// Reusable numeric text input component
// --------------------------------------------------

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
        type="text"
        inputMode={step === '1' ? 'numeric' : 'decimal'}
        autoComplete="off"
        value={value}
        onChange={onChange}
        required
      />
    </div>
  )
}

// --------------------------------------------------
// Main Dashboard
// --------------------------------------------------

function Dashboard() {
  const [values, setValues] = useState({ ...initialValues })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Update input values
  const updateValue = (event) => {
    const { name, value } = event.target

    setValues((previous) => ({
      ...previous,
      [name]: value,
    }))

    setResult(null)
    setError('')
  }

  // ------------------------------------------------
  // Input validation
  // ------------------------------------------------

  const validateInputs = () => {
    const numericFields = [
      { name: 'age', label: 'Age', min: 15, max: 80 },
      { name: 'albumin', label: 'Albumin', min: 1.8, max: 5.0 },
      { name: 'bmi', label: 'BMI', min: 12, max: 35 },
    ]

    for (const field of numericFields) {
      const value = values[field.name].trim()

      if (value === '') {
        return `${field.label} cannot be empty.`
      }

      const number = Number(value)

      if (!Number.isFinite(number)) {
        return `Please enter a valid number for ${field.label}.`
      }

      if (number < field.min || number > field.max) {
        return `${field.label} must be between ${field.min} and ${field.max}.`
      }
    }

    return ''
  }

  // ------------------------------------------------
  // Generate demonstration prediction
  // ------------------------------------------------

  const handleSubmit = async (event) => {
    event.preventDefault()

    const validationError = validateInputs()

    if (validationError) {
      setError(validationError)
      setResult(null)
      return
    }

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
          ? 'Cannot connect to the demonstration API. Make sure the FastAPI server is running.'
          : err.message
      )
    } finally {
      setLoading(false)
    }
  }

  // ------------------------------------------------
  // Reset inputs
  // ------------------------------------------------

  const handleReset = () => {
    setValues({ ...initialValues })
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

        {/* Synthetic data warning */}

        <div className="notice">
          <div className="notice-icon">!</div>

          <p>
            <strong>IMPORTANT: SYNTHETIC DATA DEMONSTRATION</strong>
            <br />
            This model was trained entirely on simulated synthetic
            data. It has not been clinically validated. All
            probabilities are illustrative software outputs, NOT
            actual medical risk estimates. Enter fictional values
            only. Never use this tool for real patient assessment,
            diagnosis or treatment decisions.
          </p>
        </div>

        <form className="dashboard-card demo-form" onSubmit={handleSubmit}>
          <div className="card-symbol">⌬</div>

          <h3>Genetic and Clinical Demonstration Inputs</h3>

          <p>
            Enter fictional illustrative values to explore how the
            demonstration model responds.
          </p>

          {/* Genetic inputs */}

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

          {/* Clinical inputs */}

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
                  { value: '0', label: 'Female' },
                  { value: '1', label: 'Male' },
                ]}
              />

              <SelectField
                label="Alcohol variable (model encoding)"
                name="alcohol"
                value={values.alcohol}
                onChange={updateValue}
                options={[
                  { value: '0', label: '0 — No' },
                  { value: '1', label: '1 — Yes' },
                ]}
              />

              <SelectField
                label="HIV variable (model encoding)"
                name="hiv"
                value={values.hiv}
                onChange={updateValue}
                options={[
                  { value: '0', label: '0 — No' },
                  { value: '1', label: '1 — Yes' },
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

          {/* Action buttons */}

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

          {/* Loading message */}

          {loading && (
            <div className="demo-result" role="status">
              Generating synthetic demonstration output...
            </div>
          )}

          {/* Error message */}

          {error && (
            <div className="demo-error" role="alert">
              {error}
            </div>
          )}

          {/* Result */}

          {result && (
            <div className="demo-result" aria-live="polite">
              <span className="eyebrow">
                SYNTHETIC DEMONSTRATION RESULT
              </span>

              <h3>Illustrative Model Probability</h3>

              <div className="demo-probability">
                {Number(result.percentage).toFixed(2)}%
              </div>

              <p>
                This percentage is a simulated output from the
                demonstration model. It must not be interpreted
                as an individual's actual medical risk.
              </p>

              <div className="demo-result-details">
                <span>Model: {result.model_name}</span>
                <span>Clinical validation: No</span>
                <span>Data type: Synthetic</span>
                <span>Medical use: Not permitted</span>
              </div>

              <div className="notice demo-disclaimer">
                <div className="notice-icon">!</div>

                <p>
                  <strong>Research demonstration only.</strong>
                  <br />
                  {result.disclaimer}
                </p>
              </div>
            </div>
          )}

          <small className="demo-footer-note">
            Synthetic educational prototype · Not clinically
            validated · Not for diagnosis, treatment decisions
            or real patient assessment.
          </small>
        </form>
      </section>
    </>
  )
}

export default Dashboard
