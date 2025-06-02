import React, { useState } from "react";

export default function SourcesBox({ sources }) {
  const [showSources, setShowSources] = useState(false);

  return (
    <div className="sources-container">
      <button className="toggle-sources" onClick={() => setShowSources(!showSources)}>
        {showSources ? "Hide Sources" : "Show Sources"}
      </button>
      {showSources && (
        <div className="sources-box">
          {sources.length > 0 ? (
            sources.map((src, i) => (
              <div>
                <p key={i}>
                  <strong>{src.title}</strong>: {src.content}
                </p><br/>
              </div>
            ))
          ) : (
            <p>No sources available.</p>
          )}
        </div>
      )}
    </div>
  );
}
