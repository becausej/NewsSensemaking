function highlightMaxSentimentSentence() {
  console.log("start");
  const current_url = window.location.toString();

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
      sent = data.max_sentence;

      temp = findElement(document, sent);
      if (!temp) {
        console.log("failed");
        return;
      }

      const highlightedWord = `<span style="background-color: yellow;">${sent}</span>`;
      temp.innerHTML = temp.innerHTML.replace(sent, highlightedWord)
      console.log("should've worked")
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
