// Listener for messages from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "getSentenceScore") {
        const sentence = message.sentence;
        
        // Fetch the score from the Flask server
        fetch("http://localhost:5000/classify_sentence", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ sentence }),
        })
            .then((response) => response.json())
            .then((data) => {
                sendResponse({ score: data.score });
            })
            .catch((error) => {
                console.error("Error fetching score:", error);
                sendResponse({ score: 0 }); // Default score in case of error
            });

        // Return true to indicate that the response is sent asynchronously
        return true;
    }
});
