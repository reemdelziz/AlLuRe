import React, { useState } from "react";
import QuestionInput from "./components/QuestionInput";
import AnswerBox from "./components/AnswerBox";
import SourcesBox from "./components/SourcesBox";
import FactSubmission from "./components/FactSubmission";
import LoadingSpinner from "./components/LoadingSpinner";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    try {
      const res = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer || "No answer.");
      setSources(data.sources || []);
    } catch (err) {
      setAnswer("⚠️ Error loading answer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="wrapper">
      <h2 className="title">United States of America Wiki</h2>
      {/* <LoadingSpinner loading={loading} /> */}
      {loading ? <LoadingSpinner />:null}
      <AnswerBox answer={answer} />
      <SourcesBox sources={sources} />
      <QuestionInput question={question} setQuestion={setQuestion} handleAsk={handleAsk} />
      <hr className="section-divider" />
      <FactSubmission />
    </div>
  );
}

export default App;
