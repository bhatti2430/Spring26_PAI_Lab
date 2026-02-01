#  Email Extractor - Flask Web Application

A beautiful Flask web application to extract emails from websites, with support for both single URL lookups and bulk CSV processing.

## Features

 **Single URL Extraction** - Enter a website URL and fetch email address  
 **Bulk CSV Processing** - Upload a CSV file and extract emails for all URLs  
 **Beautiful UI** - Modern, responsive web interface  
 **Download Results** - Export results as CSV files  
 **Robust Email Detection** - Searches webpage text and links for email addresses  
 **Retry Logic** - Handles network issues automatically  

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Project Structure

Your project should have this structure:
```
📁 Tasks/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── email.csv                       # Your CSV file (optional)
├── 📁 templates/
│   └── index.html                  # Main HTML page
└── 📁 static/
    ├── style.css                   # Styling
    └── script.js                   # Frontend logic
```

## Usage

### Starting the Application

```bash
python app.py
```

The application will start at: **http://localhost:5000**

### Single URL Mode

1. Go to the "Single URL" tab
2. Enter a website URL (e.g., `https://example.com` or just `example.com`)
3. Click "Fetch Email" button
4. View the extracted email
5. Click "Download CSV" to save the result

### Bulk CSV Mode

1. Go to the "Upload CSV" tab
2. Select your CSV file (must have a column named "url", "website", "link", or similar)
3. Click "Process CSV" button
4. Wait for the extraction to complete
5. View all results
6. Click "Download Updated CSV" to save the results with email column

## CSV File Format

Your CSV file should have at least one column with website URLs:

| company | url | industry |
|---------|-----|----------|
| Company A | https://example1.com | Tech |
| Company B | example2.com | Finance |

The application will add an "email" column with extracted email addresses.

## How It Works

1. **Fetches** the website content
2. **Searches** for email patterns in:
   - Page text content
   - Links and href attributes
   - Meta tags
3. **Returns** the first valid email found or "Not Found"
4. **Downloads** results as a downloadable CSV file

## Example Results

**Single URL Result:**
- URL: `https://example.com`
- Email: `contact@example.com`

**Bulk Results:**
```csv
company,url,email
Company A,https://example1.com,info@example1.com
Company B,example2.com,Not Found
Company C,https://example3.com,support@example3.com
```

## Error Handling

The application handles:
- Invalid URLs
- Network timeouts
- Missing email columns in CSV
- File encoding issues
- HTTP errors (with automatic retries)

## Troubleshooting

**"No URL column found"**
- Ensure your CSV has a column named "url", "website", "site", or "link"

**"File too large"**
- Maximum file size is 16MB

**"Connection timeout"**
- The website may be blocking requests or be offline
- Check the URL and try again

**"CSV not opening"**
- Ensure the file is a valid CSV format
- Check encoding (UTF-8, CP1252, etc.)

## Features

-  **Fast Processing** - Parallel-like processing with polite delays
-  **Retry Logic** - Automatic retries for failed requests
-  **CSV Support** - Multiple encoding formats supported
-  **Modern UI** - Responsive design works on mobile and desktop
-  **Download** - Export results instantly
-  **Real-time** - See results as they're processed

## Performance Tips

- Use shorter timeout for faster feedback
- Upload smaller CSV files (< 1000 rows recommended)
- Add 1-second delay between requests to be polite to servers
- Avoid extracting during peak hours if processing many URLs

## License

Free to use and modify for your needs.

---

