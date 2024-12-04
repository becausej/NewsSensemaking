// // set popup information
document.addEventListener("DOMContentLoaded", async function () {
    // sentiment
    //getTitle();
    getSentiment();
    getAllsides();
    getSmog();
    getFullTextClass();
    getBiasIndicator();
    // etc.
});

function getFullTextFromPage() {
    return new Promise((resolve, reject) => {
      function extractMainTextBody() {
        const selectors = [
          'article',
          'div[class*="content"]',
          'div[class*="article"]',
          'main',
          'body'
        ];
  
        let textBody = '';
  
        for (const selector of selectors) {
          const element = document.querySelector(selector);
          if (element) {
            textBody = element.innerText.trim();
            if (textBody) break;
          }
        }
  
        return textBody || 'No main text content found on this page.';
      }
  
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (!tabs || tabs.length === 0) {
          reject("No active tab found.");
          return;
        }
  
        const tab = tabs[0];
  
        chrome.scripting.executeScript(
          {
            target: { tabId: tab.id },
            func: extractMainTextBody,
          },
          (results) => {
            if (chrome.runtime.lastError) {
              reject(`Script injection failed: ${chrome.runtime.lastError.message}`);
            } else if (results && results[0] && results[0].result) {
              resolve(results[0].result);
            } else {
              reject("No text content extracted.");
            }
          }
        );
      });
    });
  }
  
async function getSentiment() {
    const current_url = await getUrl();
    if (!current_url) {
        return;
    }

    fetch("http://127.0.0.1:5000/get_analysis", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: current_url }),
    })
        .then((response) => response.json())
        .then((data) => {
            document_sentiment = data.total_sentiment;
            console.log("sentiment", document_sentiment);
            if (document_sentiment) {
                const formatted = (document_sentiment + 1) * 50;
                setIndicator("sentiment-indicator", formatted);
                return document_sentiment;
            }
        })
        .catch((error) => console.error("Error:", error));
    return 0;
}

async function getAllsides() {
    const current_url = await getUrl();
    if (!current_url) {
        return;
    }

    fetch("http://127.0.0.1:5000/allsides_rating", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: current_url }),
    })
        .then((response) => response.json())
        .then((data) => {
            document_rating = data.allsides_rating;
            if (document_rating) {
                setIndicator("political-level-indicator", document_rating);
            }
        })
        .catch((error) => console.error("Error:", error));
}

async function getSmog() {
    console.log("sup");
    const current_text = await getFullTextFromPage();
    console.log("found text for smogging")
    if (!current_text) {
        console.log("ERROR GETTING TEXT")
        return;
    }
    console.log("hello");
    fetch("http://127.0.0.1:5000/smog_full_text", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: current_text }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log("smog", data.smog_score);
            document_smog = data.smog_score;
            if (document_smog) {
                console.log("smog", data.smog_score);
                document.getElementById("reading-level").textContent =
                    document_smog;
            }
        })
        .catch((error) => console.error("Error:", error));
}

async function getFullTextClass() {
    const current_text = await getFullTextFromPage();
    console.log("found text for classification")
    if (!current_text) {
        console.log("ERROR GETTING TEXT")
        return;
    }
    fetch("http://127.0.0.1:5000/classify_full_text", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: current_text }),
    })
        .then((response) => response.json())
        .then((data) => {
            document_class = data.class;
            if (document_class) {
                document.getElementById("reliable").textContent =
                    document_class;
            }
        })
        .catch((error) => console.error("Error:", error));
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
            chrome.tabs.sendMessage(
                tabs[0].id,
                { action: "getTitle" },
                (response) => {
                    if (response && response.title) {
                        console.log("title", response.title);
                        document.getElementById("article-title").textContent =
                            response.title;
                        resolve(response.title);
                    } else {
                        console.error("Failed to get the title");
                        reject("Failed to get the title");
                    }
                }
            );
        });
    });
}

async function getBiasIndicator() {
    const current_url = await getUrl();
    if (!current_url) {
        return;
    }

    fetch("http://127.0.0.1:5000/bias_indicator", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: current_url }),
    })
        .then((response) => response.json())
        .then((data) => {
            document_rating = data.score;
            if (document_rating) {
                setIndicator("bias-indicator-indicator", document_rating);
                console.log("bias: ", document_rating);
            }
        })
        .catch((error) => console.error("Error:", error));
}

document.addEventListener("DOMContentLoaded", function () {
    // Replace the placeholders with actual data
    document.getElementById("reading-level").textContent = "...";
    document.getElementById("reliable").textContent = "...";

    // Set indicator positions based on some value (0 to 100)
    const politicalLevel = 50; // Example value
    const biasIndicator = 50; // Example value
    const sentiment = 50; // Example value

    setIndicator("political-level-indicator", politicalLevel);
    setIndicator("bias-indicator-indicator", biasIndicator);
    setIndicator("sentiment-indicator", sentiment);
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
document.addEventListener("change", function (event) {
    if (event.target.name === "global-option") {
        console.log(`Global option selected: ${event.target.value}`);
        // Add your logic here
    }
});

// Save state when the radio button is changed
document.addEventListener("change", function (event) {
    if (event.target.name === "global-option") {
        chrome.storage.sync.set({ globalOption: event.target.value });
    }
});

// Load the saved state when the popup is opened
document.addEventListener("DOMContentLoaded", function () {
    chrome.storage.sync.get("globalOption", function (data) {
        const globalOption = data.globalOption;
        if (globalOption) {
            const radioButton = document.querySelector(
                `input[name="global-option"][value="${globalOption}"]`
            );
            if (radioButton) {
                radioButton.checked = true;
            }
        }
    });
});