import React, { useState } from "react";

export default function FactSubmission() {
  const [isOpen, setIsOpen] = useState(false);
  const [fact, setFact] = useState("");
  const [source, setSource] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const toggleSubmission = () => {
    setIsOpen(!isOpen);
    setIsSubmitted(false);
  };

  const handleSubmit = async () => {
    if (!fact.trim()) return alert("Please enter a fact.");
    if (!source) return alert("Please select a source type.");
    // const response = await fetch("http://localhost:5000/submit", {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({ fact, source }),
    // });
    // const data = await response.json();
    // alert(data.message);
    setFact("");
    setSource("");
    setIsSubmitted(true);
  };

  return (
    <div className="submit-container">
      <button className="toggle-submission" onClick={toggleSubmission}>
        <h3 className="submit-title">Contribute A Source</h3>
      </button>

      {isOpen ? isSubmitted ?
        (
        <div className="submit-section">
          <p>Thank you! Your submission is under review.</p>
        </div>
        ):
        (
        <div className="submit-section">
          <textarea
            id="userFact"
            placeholder="Submit a fact..."
            value={fact}
            onChange={(e) => setFact(e.target.value)}
            className="submit-input"
          />

          <p className="source-question">What are you submitting?</p>
          
          <div className="source-select">
            <label>
              <input
                type="radio"
                name="source"
                value="WikiPage"
                checked={source === "WikiPage"}
                onChange={(e) => setSource(e.target.value)}
              />
              Wiki Page Title
            </label><br/><br/>
            <label>
              <input
                type="radio"
                name="source"
                value="DirectFact"
                checked={source === "DirectFact"}
                onChange={(e) => setSource(e.target.value)}
              />
              Direct Content or Fact
            </label><br/><br/>

          </div>

          <button onClick={handleSubmit} className="submit-btn">
            Submit
          </button>
        </div>
        )
      :null}


      
    </div>
  );
}
