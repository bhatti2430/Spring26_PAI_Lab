// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Handle single URL form
async function handleSingleURL(event) {
    event.preventDefault();
    
    const url = document.getElementById('url').value.trim();
    const resultDiv = document.getElementById('singleResult');
    const errorDiv = document.getElementById('singleError');
    const loadingDiv = document.getElementById('singleLoading');
    
    // Clear previous results
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'flex';
    
    try {
        const response = await fetch('/api/fetch-single', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error fetching email');
        }
        
        // Store data for download
        window.singleURLData = {
            url: data.url,
            email: data.email
        };
        
        document.getElementById('resultUrl').textContent = data.url;
        document.getElementById('resultEmail').textContent = data.email;
        
        loadingDiv.style.display = 'none';
        resultDiv.style.display = 'block';
        errorDiv.style.display = 'none';
        
    } catch (error) {
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = '❌ ' + error.message;
    }
}

// Handle bulk CSV form
async function handleBulkCSV(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showBulkError('Please select a CSV file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    document.getElementById('bulkResults').style.display = 'none';
    document.getElementById('bulkError').style.display = 'none';
    document.getElementById('bulkLoading').style.display = 'flex';
    
    try {
        const response = await fetch('/api/fetch-csv', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error processing CSV');
        }
        
        // Store CSV data for download
        window.bulkCSVData = data.csv_data;
        
        displayBulkResults(data.results);
        
        document.getElementById('bulkLoading').style.display = 'none';
        document.getElementById('bulkResults').style.display = 'block';
        document.getElementById('bulkError').style.display = 'none';
        
    } catch (error) {
        showBulkError(error.message);
        document.getElementById('bulkLoading').style.display = 'none';
    }
}

// Display bulk results
function displayBulkResults(results) {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '';
    
    results.forEach(result => {
        const row = document.createElement('div');
        row.className = 'result-row';
        
        const isError = result.email.includes('Error') || result.email === 'Not Found';
        
        row.innerHTML = `
            <div>
                <div class="result-row-header">#${result.index}/${result.total}</div>
                <div class="result-row-progress">${result.index}/${result.total}</div>
            </div>
            <div class="result-row-url">
                <div class="result-row-header">URL</div>
                ${result.url}
            </div>
            <div class="result-row-email ${isError ? 'error' : ''}">
                <div class="result-row-header" style="color: inherit; margin-bottom: 3px;">Email</div>
                ${result.email}
            </div>
        `;
        
        resultsList.appendChild(row);
    });
}

// Show bulk error
function showBulkError(message) {
    const errorDiv = document.getElementById('bulkError');
    errorDiv.style.display = 'block';
    errorDiv.textContent = '❌ ' + message;
}

// Download single URL result
async function downloadSingleCSV() {
    if (!window.singleURLData) return;
    
    try {
        const response = await fetch('/download-single-csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(window.singleURLData)
        });
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const blob = await response.blob();
        downloadBlob(blob, 'email_result.csv');
        
    } catch (error) {
        alert('Error downloading file: ' + error.message);
    }
}

// Download bulk CSV results
async function downloadBulkCSV() {
    if (!window.bulkCSVData) return;
    
    try {
        const response = await fetch('/download-csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ csv_data: window.bulkCSVData })
        });
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const blob = await response.blob();
        downloadBlob(blob, 'emails_extracted.csv');
        
    } catch (error) {
        alert('Error downloading file: ' + error.message);
    }
}

// Helper function to download blob
function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
