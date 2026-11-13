export default function Home({ onStart }) {
  return (
    <div className="home">
      <div className="glass hero">
        <span className="badge">● online</span>
        <h1>Student Helper</h1>
        <p className="lead">
          Ask questions about your course material and get answers with sources.
        </p>
        <button className="cta" onClick={onStart}>Start asking →</button>
        <p className="privacy">
          Questions and feedback are recorded anonymously to improve this tool.
          Please don't include your name or personal details.
        </p>
      </div>

      <div className="features">
        <div className="glass card">
          <h3>Grounded</h3>
          <p>Answers come from your course PDFs, not from guesswork.</p>
        </div>
        <div className="glass card">
          <h3>Cited</h3>
          <p>Every answer shows which file and page it came from.</p>
        </div>
        <div className="glass card">
          <h3>Improving</h3>
          <p>Your thumbs up or down helps make it better.</p>
        </div>
      </div>
    </div>
  );
}