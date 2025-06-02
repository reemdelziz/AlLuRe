import React from "react";

export default function AnswerBox({ answer, confidence }) {
  return (
    <div>
      <div id="answerBox" className="answer-box">
        {answer}
      </div>
      <div className="confidenceScore">
        Confidence [0-1]: <strong>{confidence}</strong>
      </div>
    </div>
      
  );
}
