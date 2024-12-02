// Sends popup the article title
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "getTitle") {
        const title = document.title;
        console.log("got title");
        sendResponse({ title });
    }
});

// Max sentiment sentence highlighting
function highlightMaxSentimentSentence() {
    console.log("start");
    const current_url = window.location.toString();
    console.log("title", document.title);

    fetch("http://127.0.0.1:5000/get_max_sentence", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: current_url }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log("sentence", data.max_sentence);
            sentence = data.max_sentence;

            node = findElement(document, sentence);
            if (!node) {
                console.log("failed");
                return;
            }
            const color = data.max_sentence_score < 0 ? "cyan" : "yellow";
            const highlightedSentence = `<span style="background-color: ${color};">${sentence}</span>`;
            node.innerHTML = node.innerHTML.replace(
                sentence,
                highlightedSentence
            );
            console.log("should've worked");
        })
        .catch((error) => console.error("Error:", error));
}

// bfs searches html for correct element node
function findElement(root, value) {
    const queue = [root];

    while (queue.length > 0) {
        const currentNode = queue.shift();

        if (currentNode.nodeType === Node.ELEMENT_NODE) {
            if (currentNode.innerText.includes(value)) {
                console.log("Found text in element:", currentNode);
                return currentNode;
            }
        }
        for (const child of currentNode.children) {
            queue.push(child);
        }
    }
}
// Function to get the score of a sentence by sending it to the background script
function getSentenceScore(sentence) {
    console.log("getting score");
    return new Promise((resolve) => {
        chrome.runtime.sendMessage(
            { action: "getSentenceScore", sentence },
            (response) => {
                if (response && typeof response.score === "number") {
                    resolve(response.score);
                } else {
                    console.log("failed to get score");
                    resolve(0); // Default score if none received
                }
            }
        );
    });
}

// Function to map a score to a background color (from white to yellow)
function getBackgroundColor(score) {
    // Assuming score is between 0 and 1
    const intensity = Math.floor(score * 255);
    return `rgb(255, 255, ${255 - intensity})`; // From white to yellow
}

// Main function to style sentences
async function styleSentences() {
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    let node;
    const textNodes = [];

    // Collect all text nodes
    while ((node = walker.nextNode())) {
        textNodes.push(node);
    }

    // Process each text node
    for (const textNode of textNodes) {
        // Skip script and style elements
        if (
            textNode.parentNode &&
            !["SCRIPT", "STYLE", "NOSCRIPT"].includes(
                textNode.parentNode.nodeName
            )
        ) {
            const sentences = textNode.nodeValue.split(/(?<=[.?!])\s+/);
            if (sentences.length > 0) {
                const fragment = document.createDocumentFragment();

                for (const sentence of sentences) {
                    const span = document.createElement("span");
                    const score = await getSentenceScore(sentence);
                    span.textContent = sentence + " ";
                    span.style.backgroundColor = getBackgroundColor(score);
                    fragment.appendChild(span);
                }

                textNode.parentNode.replaceChild(fragment, textNode);
            }
        }
    }
}

// Initialize the script
function init() {
    // styleSentences();
    //highlightMaxSentimentSentence();
}

// Run the init function when the DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
