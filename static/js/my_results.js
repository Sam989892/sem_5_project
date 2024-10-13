document.addEventListener('DOMContentLoaded', function() {
    const resultsList = document.getElementById('results-list');
    const currentUser = localStorage.getItem('currentUser');

    if (!currentUser) {
        window.location.href = '/';
        return;
    }

    // Fetch results from server
    fetch(`/get_results/${currentUser}`)
        .then(response => response.json())
        .then(userResults => {
            if (userResults.length === 0) {
                resultsList.innerHTML = '<p>No saved results found.</p>';
            } else {
                let resultsHTML = '<ul>';
                userResults.forEach((savedResult, index) => {
                    resultsHTML += `
                        <li>
                            <h3>Result ${index + 1}</h3>
                            <p>Date: ${new Date(savedResult.timestamp).toLocaleString()}</p>
                            <ul>
                            ${savedResult.results.map(result => `
                                <li>
                                    <p>Text: ${result.text}</p>
                                    <p>Sentiment: ${result.sentiment}</p>
                                    <p>Strength: ${result.strength}</p>
                                </li>
                            `).join('')}
                            </ul>
                        </li>
                    `;
                });
                resultsHTML += '</ul>';
                resultsList.innerHTML = resultsHTML;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultsList.innerHTML = '<p>An error occurred while fetching results.</p>';
        });
});
