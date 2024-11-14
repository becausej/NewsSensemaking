
function highlightFirstWord() {
  const mainContent = document.querySelector('.mw-body');
  
  if (!mainContent) return; 
  
  const bodyText = mainContent.innerText;

  if (!bodyText) return;

  fetch('http://127.0.0.1:5000/get_data')
    .then(response => response.json())
    .then(data => {
      console.log("Data from Flask:", data.message);
    })
    .catch(error => console.error("Error:", error));

  fetch('http://127.0.0.1:5000/process_text', {
      method: 'POST', 
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: bodyText })
  })
  .then(response => response.json())
  .then(data => {
      // TODO
  })
  .catch(error => console.error('Error:', error));

  const firstWordMatch = bodyText.match(/\b\w+\b/); 

  if (firstWordMatch) {
      const firstWord = firstWordMatch[0];

      const highlightedWord = `<span style="background-color: yellow;">${firstWord}</span>`;

      mainContent.innerHTML = mainContent.innerHTML.replace(firstWord, highlightedWord);
  }
}

// Run the function when the page has loaded
highlightFirstWord();
