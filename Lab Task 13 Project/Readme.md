# Real-Time Background Removal Application

A Python-based application that uses OpenCV to remove and replace video backgrounds in real-time. This project can be integrated with video conferencing applications like Zoom and Microsoft Teams.

## Features

- Real-time background removal and replacement
- Works with webcam input
- Support for custom background images
- Flask web interface for easy access
- Keyboard controls for easy operation
- Compatible with video conferencing applications

## Prerequisites

- Python 3.7 or higher
- Webcam
- Windows/Linux/Mac

## Installation

1. **Install Dependencies**
   
   Option A - Using batch file (Windows):
   ```bash
   libraries.bat
   ```
   
   Option B - Using pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Installation**
   
   Check that all packages are installed correctly before proceeding.

## Usage

### Desktop Application
Run the desktop version with:
```bash
python main.py
```

### Web Application
Run the Flask backend:
```bash
python app.py
```

Then access the application through your web browser.

## Controls

| Key | Action |
|-----|--------|
| **a** | Previous background image |
| **d** | Next background image |
| **q** | Quit application |

## Troubleshooting

### Webcam Not Detected

If your webcam is not showing or you get errors:

1. Modify the camera index in `main.py`:
   ```python
   cap = cv2.VideoCapture(0)  # Change 0 to 1, 2, etc.
   ```

2. Try incrementing the number (0 → 1 → 2) until your webcam is detected.

### Custom Background Images

All background images should be placed in the `img/` folder.

**Image Requirements:**
- Resolution: 640×480 pixels (recommended)
- Supported formats: JPG, PNG, JFIF

To use different resolutions, modify these parameters:
```python
cap.set(3, 640)   # Width
cap.set(4, 480)   # Height
```

## Advanced Configuration

### Hide Original Video

To display only the background without the original video overlay:

Uncomment or modify these lines in the code:
```python
# imgStacked = cvzone.stackImages([img, imgOut], 2, 1)
# _, imgStacked = fpsReader.update(imgStacked, color=(255, 0, 255))

# Show only the processed output
cv2.imshow("Image", imgOut)
```

## Project Structure

```
.
├── main.py              # Desktop application
├── app.py               # Flask web application
├── requirements.txt     # Python dependencies
├── libraries.bat        # Windows installation script
├── img/                 # Background images folder
├── static/              # Web assets (CSS, JS)
└── templates/           # HTML templates
```

## Technologies Used

- **OpenCV** - Computer vision library
- **Flask** - Web framework
- **CVZone** - OpenCV utilities
- **Python** - Programming language

## License

This project is open source and available for educational purposes.

## Notes

- Ensure your webcam is properly connected and not in use by other applications
- The background removal quality depends on lighting conditions
- For best results, ensure good lighting and clear background separation