// Sends popup the article title
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "getTitle") {
    const title = document.title;
    console.log("got title")
    sendResponse({ title });
  }
});

// Max sentiment sentence highlighting
function highlightMaxSentimentSentence() {
  console.log("start");
  const current_url = window.location.toString();
  console.log("title", document.title);

  fetch('http://127.0.0.1:5000/get_max_sentence', {
      method: 'POST', 
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: current_url })
  })
  .then(response => response.json())
  .then(data => {
      console.log("sentence", data.max_sentence);
      sentence = data.max_sentence;

      node = findElement(document, sentence);
      if (!node) {
        console.log("failed");
        return;
      }

      const color = data.max_sentence_score < 0 ? "blue" : "yellow";
      const highlightedSentence = `<span style="background-color: ${color};">${sentence}</span>`;
      //node.innerHTML = node.innerHTML.replace(sentence, highlightedSentence);
      console.log("should've worked");
  })
  .catch(error => console.error('Error:', error));
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

// Run the function when the page has loaded
highlightMaxSentimentSentence();
