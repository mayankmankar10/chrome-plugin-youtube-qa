document.getElementById("submitBtn").addEventListener("click", async () => {
    const url = document.getElementById("youtubeLink").value.trim();
    const question = document.getElementById("question").value.trim();
    const responseDiv = document.getElementById("response");
    const loader = document.getElementById("loader");

    if (!url || !question) {
        responseDiv.textContent = "Please enter both a URL and a question.";
        return;
    }

    // Show loader and clear previous response
    loader.style.display = "block";
    responseDiv.style.display = "none";
    responseDiv.innerHTML = "";

    try {
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
    } finally {
        // Hide loader and show response
        loader.style.display = "none";
        responseDiv.style.display = "block";
    }
});
