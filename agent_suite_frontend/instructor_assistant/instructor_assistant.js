document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const responseOutput = document.getElementById('response-output');
    const loadingIndicator = document.getElementById('loading-indicator');

    // Define the backend API endpoint for file uploads
    const API_URL = 'http://127.0.0.1:8000/api/instructor_assistant/analyze_feedback';

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            responseOutput.textContent = 'Please select a file to upload.';
            responseOutput.style.color = '#ef4444'; // Red color for error
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // Show loading indicator and clear previous output
        loadingIndicator.classList.remove('hidden');
        responseOutput.textContent = '';
        responseOutput.style.color = ''; // Reset color

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData,
                // Note: 'Content-Type' header is not set manually for FormData.
                // The browser sets it automatically with the correct boundary.
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            // Check if the response matches the FeedbackAnalysisResponse structure
            if (data.summary && data.sentiment && Array.isArray(data.action_suggestions)) {
                let suggestionsHtml = data.action_suggestions.map(suggestion => `<li>${suggestion}</li>`).join('');
                responseOutput.innerHTML = `
                    <div class="report">
                        <h3 class="report-title">Feedback Analysis Report</h3>

                        <div class="report-section">
                            <h4 class="section-title">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
                                <span>Summary</span>
                            </h4>
                            <p class="section-content">${data.summary}</p>
                        </div>

                        <div class="report-section">
                            <h4 class="section-title">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
                                <span>Overall Sentiment</span>
                            </h4>
                            <div class="section-content">
                                <span class="sentiment-badge sentiment-${data.sentiment.toLowerCase()}">${data.sentiment}</span>
                            </div>
                        </div>

                        <div class="report-section">
                            <h4 class="section-title">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.73 18a2.62 2.62 0 0 1-1.73 1H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10l-2.05-2.05a2.62 2.62 0 0 1-1.73-1H6"></path></svg>
                                <span>Actionable Suggestions</span>
                            </h4>
                            <ul class="section-content suggestion-list">
                                ${suggestionsHtml}
                            </ul>
                        </div>
                    </div>
                `;
            } else {
                responseOutput.textContent = data.response || 'Received an unexpected response format from the server.';
            }

        } catch (error) {
            console.error('Error during file upload:', error);
            responseOutput.textContent = 'An error occurred while uploading the file. Please ensure the backend is running and check the console for details.';
            responseOutput.style.color = '#ef4444';
        } finally {
            // Hide loading indicator
            loadingIndicator.classList.add('hidden');
            // Clear the file input for the next upload
            uploadForm.reset();
        }
    });
});