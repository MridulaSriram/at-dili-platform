
function About() {
  const creators = [
    {
      name: 'M Samanvitha',
      registerNumber: 'RA9011009020072',
      linkedin: 'https://www.linkedin.com/in/samanvitha-m-349141426/',
    },
    {
      name: 'Mayukha Andukuri',
      registerNumber: 'RA2511009020085',
      linkedin: 'https://www.linkedin.com/in/mayukha-andukuri-b9b846386/',
    },
    {
      name: 'Mridula S',
      registerNumber: 'RA2511009020087',
      linkedin: 'https://www.linkedin.com/in/mridula-sriram-06721442b/',
    },
    {
      name: 'Deksita Sasikumar',
      registerNumber: 'RA2511009020090',
      linkedin: 'https://www.linkedin.com/in/deksita-sasikumar-344554377/',
    },
    {
      name: 'Ria Manuela Antony',
      registerNumber: 'RA2511009020095',
      linkedin: 'https://www.linkedin.com/in/ria-manuela-antony-768529414/',
    },
  ]

  return (
    <section className="about-section" id="about">
      <span className="eyebrow">ABOUT THE PROJECT</span>
      <h2>What is AT-DILI?</h2>

      <p>
        Anti-tubercular drug-induced liver injury (AT-DILI) is liver
        injury associated with medicines used to treat tuberculosis.
        Genetic variation is one area researchers study to understand
        why people may respond differently to these medicines.
      </p>

      <div className="info-grid">
        <article className="info-card">
          <span className="info-number">01</span>
          <h3>Genetic Variation</h3>
          <p>
            Genetic variants may influence how the body processes or
            responds to certain medicines.
          </p>
        </article>

        <article className="info-card">
          <span className="info-number">02</span>
          <h3>Research and Evidence</h3>
          <p>
            Studying associations between genetic variants and drug
            responses can support pharmacogenomics research.
          </p>
        </article>

        <article className="info-card">
          <span className="info-number">03</span>
          <h3>Model Development</h3>
          <p>
            This project aims to present the output of a separately
            developed prediction model once it becomes available.
          </p>
        </article>
      </div>

      <div className="creators-section">
        <span className="eyebrow">THE PEOPLE BEHIND THE PROJECT</span>
        <h2>Project Creators</h2>

        <p className="creators-intro">
          An academic project by students of B.Tech Biotechnology
          at SRM Institute of Science and Technology, Ramapuram.
        </p>

        <div className="creators-grid">
          {creators.map((creator, index) => (
            <article
              className="creator-card"
              key={creator.registerNumber}
              style={{
                textAlign: 'center',
                ...(index === 4
                  ? {
                      gridColumn: '1 / -1',
                      justifySelf: 'center',
                      width: 'calc(50% - 0.5rem)',
                    }
                  : {}),
              }}
            >
              <h3>{creator.name}</h3>

              <p className="creator-register">
                ({creator.registerNumber})
              </p>

              <a
                className="creator-link"
                href={creator.linkedin}
                target="_blank"
                rel="noopener noreferrer"
              >
                LinkedIn Profile ↗
              </a>
            </article>
          ))}
        </div>

        <div className="institution-card">
          <div>
            <h3>B.Tech Biotechnology</h3>
            <p>SRM Institute of Science and Technology</p>
            <p>Ramapuram Campus</p>
          </div>
        </div>
      </div>

      <p className="disclaimer">
        <strong>Research disclaimer:</strong> This website is an academic
        prototype, not a medical diagnostic tool. Any future model output
        must be interpreted within its validated scope and with
        appropriate clinical guidance.
      </p>
    </section>
  )
}

export default About
