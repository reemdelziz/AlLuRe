const wrapper = document.querySelector(".wrapper");
const question = document.querySelector(".question");
const gif = document.querySelector(".gif")
const qBox = document.querySelector(".question-box");
const sub = document.querySelector(".send")
let count = 0

function displayAnswer(answer, sources, confidence) {
    document.getElementById('answerBox').textContent = answer;

    const sourcesBox = document.getElementById('sourcesBox');
    sourcesBox.innerHTML = ''; // Clear previous content

    sources.forEach((src, index) => {
        const p = document.createElement('p');
        p.innerHTML = `
        <strong>${index + 1}. ${src.title}</strong><br/>
        ${src.content}
        `;
        sourcesBox.appendChild(p);
    });
}

function toggleSources() {
    const box = document.getElementById('sourcesBox');
    const button = document.querySelector('.toggle-sources');
    if (box.style.display === 'none' || box.style.display === '') {
        box.style.display = 'block';
        button.textContent = 'Hide Sources';
    } else {
        box.style.display = 'none';
        button.textContent = 'Show Sources';
    }
}

function submitFact() {
  const fact = document.getElementById("userFact").value;
  const source = document.getElementById("userSource").value || "User Submission";

  fetch('/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fact, source })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
  });
}

function toggleSubmission() {
    const box = document.getElementById('submitBox');
    // const button = document.querySelector('.toggle-submission');
    if (box.style.display === 'none' || box.style.display === '') {
        box.style.display = 'flex';
        // button.textContent = 'Hide Sources';
    } else {
        box.style.display = 'none';
        // button.textContent = 'Show Sources';
    }
}


// qBox.addEventListener("keydown", function (e) {
//     if (e.code === "Enter") {
//         ValidityState(e);
//         question.style.display === "none";
//     }
// });

sub.addEventListener("click", () => {
    const userQuestion = qBox.value.trim();
    if (userQuestion === "") return;

    // Show loading spinner
    const loading = document.getElementById("loadingIndicator");
    loading.style.display = "block"; 
    const response = document.getElementById("answerBox");
    response.style.display = "none";

    fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: userQuestion })
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = "none"; // ✅ Hide spinner here
        response.style.display = "block"; // ✅ Show response here

        console.log("Answer:", data.answer);

        const answer = data.answer || "No answer returned.";
        const sources = data.sources || [];
        const confidence = data.confidence || 0;

        // Display the answer on the page
        displayAnswer(answer, sources, confidence);
    })
    .catch(err => {
        console.error("Error calling backend:", err);
        document.getElementById("answerBox").textContent = "⚠️ Error loading answer.";
    });

});