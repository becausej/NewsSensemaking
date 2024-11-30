// set popup information
document.addEventListener('DOMContentLoaded', async function () {
  // sentiment
  getSentiment(); 
  // etc.
});

async function getSentiment() {
  const current_url = await getUrl(); 
  if (!current_url) {
    return;
  }

  fetch('http://127.0.0.1:5000/get_analysis', {
      method: 'POST', 
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: current_url })
  })
  .then(response => response.json())
  .then(data => {
      document_sentiment = data.total_sentiment;
      console.log("sentiment", document_sentiment);
      if (document_sentiment) {
        const sentimentElement = document.getElementById('sentiment_value'); // i dont love that the ui logic is here (TODO?)
        sentimentElement.textContent = document_sentiment.toFixed(3);
        return document_sentiment;
      }
  })
  .catch(error => console.error('Error:', error));
  return 0;
}

function getUrl() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0) {
          const current_url = tabs[0].url;
          resolve(current_url);
      } else {
        reject("Url not found");
      }
    });
  });
}

function getTitle() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: "getTitle" }, (response) => {
        if (response && response.title) {
          console.log("title", response.title)
          resolve(response.title);
        } else {
          console.error("Failed to get the title");
          reject("Failed to get the title")
        }
      });
    });
  });
}