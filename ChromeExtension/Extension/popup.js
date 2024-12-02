// // set popup information
document.addEventListener('DOMContentLoaded', async function () {
  // sentiment
  getSentiment();
  getAllsides();
  getSmog();
  getFullTextClass();
  getTitle();
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
        const formatted = (document_sentiment + 1) * 50
        setIndicator('sentiment-indicator', formatted);
        return document_sentiment;
      }
  })
  .catch(error => console.error('Error:', error));
  return 0;
}

async function getAllsides() {
  const current_url = await getUrl(); 
  if (!current_url) {
    return;
  }

  fetch('http://127.0.0.1:5000/allsides_rating', {
      method: 'POST', 
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: current_url })
  })
  .then(response => response.json())
  .then(data => {
      
      document_rating = data.allsides_rating;
      if (document_rating) {
        setIndicator('political-level-indicator', document_rating);
      }
  })
  .catch(error => console.error('Error:', error));
}

async function getSmog() {
  const current_url = await getUrl(); 
  if (!current_url) {
    return;
  }

  fetch('http://127.0.0.1:5000/smog_full_text', {
      method: 'POST', 
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: current_url })
  })
  .then(response => response.json())
  .then(data => {
      
      document_smog = data.smog_score;
      if (document_smog) {
        document.getElementById('reading-level').textContent = document_smog;
      }
  })
  .catch(error => console.error('Error:', error));
}

async function getFullTextClass() {
  const current_url = await getUrl(); 
  if (!current_url) {
    return;
  }

  fetch('http://127.0.0.1:5000/classify_full_text', {
      method: 'POST', 
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: current_url })
  })
  .then(response => response.json())
  .then(data => {
      
      document_class = data.class;
      if (document_class) {
        document.getElementById('reliable').textContent = document_class;
      }
  })
  .catch(error => console.error('Error:', error));
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
          document.getElementById('article-title').textContent = response.title;
          resolve(response.title);
        } else {
          console.error("Failed to get the title");
          reject("Failed to get the title")
        }
      });
    });
  });
}


document.addEventListener('DOMContentLoaded', function() {
  // Replace the placeholders with actual data
  document.getElementById('article-title').textContent = "...";
  document.getElementById('reading-level').textContent = "Reading Level: 8th Grade";
  document.getElementById('reliable').textContent = "Reliable: Yes";
  
  // Set indicator positions based on some value (0 to 100)
  const politicalLevel = 50; // Example value
  const biasIndicator = 50; // Example value
  const sentiment = 50; // Example value

  setIndicator('political-level-indicator', politicalLevel);
  setIndicator('bias-indicator-indicator', biasIndicator);
  setIndicator('sentiment-indicator', sentiment);
});

/**
* Sets the position of the indicator line within the bar.
* @param {string} elementId - The ID of the indicator line element.
* @param {number} value - The value (0 to 100) indicating the position.
*/
function setIndicator(elementId, value) {
  const indicator = document.getElementById(elementId);
  if (indicator) {
      // Ensure value is between 0 and 100
      const clampedValue = Math.max(0, Math.min(100, value));
      indicator.style.left = `calc(${clampedValue}% - 1px)`; // Subtract half of the line width for centering
  }
}

// Handle global radio button selections
document.addEventListener('change', function(event) {
  if (event.target.name === 'global-option') {
      console.log(`Global option selected: ${event.target.value}`);
      // Add your logic here
  }
});
