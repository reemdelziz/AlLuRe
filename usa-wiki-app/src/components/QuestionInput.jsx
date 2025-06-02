import React from "react";

export default function QuestionInput({ question, setQuestion, handleAsk }) {
  return (
    <div className="question-group">
      <input
        type="text"
        className="question-box"
        placeholder="Ask a question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button className="send" onClick={handleAsk}>Submit</button>
    </div>
  );
}
