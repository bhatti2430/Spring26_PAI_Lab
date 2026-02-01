import os
import csv
import time
import re
import requests
from flask import Flask, render_template, request, send_file, jsonify
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry
from io import StringIO, BytesIO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup requests session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}


def extract_email_from_url(url):
    """Extract email from a single URL"""
    if not url:
        return "No URL"

    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    try:
        r = session.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Gather page text and mailto hrefs
        text = soup.get_text(separator=" ")
        hrefs = " ".join(a.get("href", "") for a in soup.find_all("a"))
        search_space = text + " " + hrefs

        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", search_space)
        unique_emails = list(dict.fromkeys(emails))  # preserve order, remove duplicates

        return unique_emails[0] if unique_emails else "Not Found"

    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/fetch-single', methods=['POST'])
def fetch_single():
    """Fetch email for a single URL"""
    try:
        url = request.json.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'Please enter a URL'}), 400
        
        email = extract_email_from_url(url)
        
        return jsonify({
            'url': url,
            'email': email,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/fetch-csv', methods=['POST'])
def fetch_csv():
    """Fetch emails for all URLs in a CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Please upload a CSV file'}), 400
        
        # Read CSV file
        stream = StringIO(file.stream.read().decode('utf-8', errors='ignore'), newline='')
        reader = csv.DictReader(stream)
        
        if not reader.fieldnames:
            return jsonify({'error': 'Invalid CSV file'}), 400
        
        fieldnames = list(reader.fieldnames)
        
        # Find URL column
        url_field = next((fn for fn in fieldnames if fn and re.search(r'url|website|site|link', fn, re.I)), None)
        if not url_field:
            return jsonify({'error': 'No URL column found. Please ensure your CSV has a column named "url", "website", etc.'}), 400
        
        # Find or create email column
        email_field = next((fn for fn in fieldnames if fn and re.search(r'email|e-mail', fn, re.I)), None)
        if not email_field:
            email_field = 'email'
            fieldnames.append(email_field)
        
        rows = []
        results = []
        total = 0
        
        # Rewind the stream and read again
        stream.seek(0)
        reader = csv.DictReader(stream)
        all_rows = list(reader)
        total = len(all_rows)
        
        for i, row in enumerate(all_rows, start=1):
            raw_url = row.get(url_field, "").strip()
            email = extract_email_from_url(raw_url)
            row[email_field] = email
            rows.append(row)
            
            results.append({
                'index': i,
                'url': raw_url,
                'email': email,
                'total': total
            })
            
            time.sleep(0.5)  # polite delay
        
        # Create CSV bytes for download
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
        csv_bytes = BytesIO(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        return jsonify({
            'results': results,
            'total': total,
            'success': True,
            'csv_data': output.getvalue()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download-csv', methods=['POST'])
def download_csv():
    """Download CSV file"""
    try:
        csv_data = request.json.get('csv_data', '')
        
        if not csv_data:
            return jsonify({'error': 'No CSV data provided'}), 400
        
        csv_bytes = BytesIO(csv_data.encode('utf-8'))
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='emails_extracted.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download-single-csv', methods=['POST'])
def download_single_csv():
    """Download single URL result as CSV"""
    try:
        data = request.json
        url = data.get('url', '')
        email = data.get('email', '')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['URL', 'Email'])
        writer.writerow([url, email])
        
        csv_bytes = BytesIO(output.getvalue().encode('utf-8'))
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='email_result.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
