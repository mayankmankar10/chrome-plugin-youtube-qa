document.getElementById("submitBtn").addEventListener("click", async () => {
    const url = document.getElementById("youtubeLink").value.trim();
    const question = document.getElementById("question").value.trim();
    const responseDiv = document.getElementById("response");
  
    if (!url || !question) {
      responseDiv.textContent = "Please enter both a URL and a question.";
      return;
    }
  
    try {
      responseDiv.textContent = "Thinking...";
  
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, question })
      });
  
      const data = await res.json();
  
      if (data.answer) {
        responseDiv.innerHTML = `<strong>Answer:</strong><br>${data.answer}`;
      } else if (data.error) {
        responseDiv.innerHTML = `❌ Error: ${data.error}`;
      } else {
        responseDiv.innerHTML = "🤷‍♂️ No answer received.";
      }
  
    } catch (error) {
      responseDiv.textContent = "Server not reachable.";
    }
  });
  