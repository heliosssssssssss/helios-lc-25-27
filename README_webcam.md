# Webcam Viewer

A simple Python program that displays your webcam feed in a window.

## Requirements

- Python 3.6 or higher
- OpenCV (cv2)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or install OpenCV directly:
```bash
pip install opencv-python
```

## Usage

Run the program:
```bash
python webcam_viewer.py
```

## Controls

- Press 'q' to quit the application
- Press Ctrl+C to force quit if needed

## Troubleshooting

- If you get "Error: Could not open webcam", make sure:
  - Your webcam is connected
  - No other application is using the webcam
  - You have the correct camera permissions
- On some systems, you might need to try different camera indices (0, 1, 2, etc.) if the default doesn't work
