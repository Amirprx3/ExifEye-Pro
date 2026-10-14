# 👁️ ExifEye Pro

**Professional Image Metadata Extractor & Analyzer with Advanced Features**

ExifEye Pro is a powerful command-line tool for extracting, analyzing, and managing image metadata (EXIF data). It offers advanced features like face detection, quality analysis, duplicate detection, privacy assessment, and much more.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

### 📊 Core Features
- **Metadata Extraction**: Extract comprehensive EXIF data from images
- **GPS Location**: Automatic reverse geocoding to human-readable locations
- **Multiple Formats**: Support for JPEG, PNG, TIFF, BMP, WebP
- **Batch Processing**: Process multiple images or entire directories
- **Export Options**: Save results as JSON or CSV

### 🔬 Advanced Analysis
- **Quality Assessment**: Analyze sharpness, brightness, contrast, and blur
- **Face Detection**: Detect and count faces in images
- **Color Analysis**: Extract dominant color palettes
- **Privacy Scanner**: Assess privacy risks in metadata
- **Duplicate Detection**: Find similar/duplicate images using perceptual hashing

### 🛡️ Privacy Tools
- **Metadata Stripping**: Remove all EXIF data for privacy
- **Privacy Risk Assessment**: Score images based on sensitive data
- **Batch Privacy Scanning**: Scan entire folders for privacy risks

### 📈 Statistics & Reports
- **Batch Statistics**: Comprehensive stats for multiple images
- **Image Comparison**: Side-by-side metadata comparison
- **Export Reports**: Generate JSON reports

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/Amirprx3/ExifEye.git
cd ExifEye

# Install dependencies
pip install -r requirements.txt

# Make it executable (Linux/Mac)
chmod +x ExifEye.py
```

### Optional: Install for Advanced Features

For face detection and quality analysis, install OpenCV:

```bash
pip install opencv-python numpy
```

---

## 📖 Usage

### Basic Commands

#### 1. Extract Metadata

```bash
# Single image
python ExifEye.py extract image.jpg

# Multiple images
python ExifEye.py extract image1.jpg image2.jpg

# Entire directory
python ExifEye.py extract /path/to/images/ --recursive

# With statistics
python ExifEye.py extract /path/to/images/ --stats

# Export to JSON
python ExifEye.py extract image.jpg --output metadata.json

# Export to CSV
python ExifEye.py extract /path/to/images/ --output data.csv --recursive
```

#### 2. Advanced Analysis

```bash
# Full analysis (quality, faces, colors, privacy)
python ExifEye.py analyze image.jpg --all

# Quality analysis only
python ExifEye.py analyze image.jpg --quality

# Face detection
python ExifEye.py analyze image.jpg --faces

# Color palette extraction
python ExifEye.py analyze image.jpg --colors

# Privacy assessment
python ExifEye.py analyze image.jpg --privacy

# Multiple images
python ExifEye.py analyze /path/to/images/ --recursive --all
```

#### 3. Find Duplicates

```bash
# Find duplicate images in a directory
python ExifEye.py duplicates /path/to/images/ --recursive

# Verbose mode for detailed output
python ExifEye.py duplicates /path/to/images/ --verbose
```

#### 4. Privacy Scanning

```bash
# Scan for privacy risks
python ExifEye.py privacy-scan /path/to/images/ --recursive

# Generate privacy report
python ExifEye.py privacy-scan /path/to/images/ --report privacy_report.json
```

#### 5. Generate Statistics

```bash
# Display batch statistics
python ExifEye.py stats /path/to/images/ --recursive

# Export statistics to JSON
python ExifEye.py stats /path/to/images/ --export stats.json
```

#### 6. Compare Images

```bash
# Compare 2 or more images side-by-side
python ExifEye.py compare image1.jpg image2.jpg image3.jpg
```

#### 7. Strip Metadata

```bash
# Remove all EXIF data from images
python ExifEye.py strip image.jpg

# Process entire directory
python ExifEye.py strip /path/to/images/ --recursive

# Custom output directory
python ExifEye.py strip /path/to/images/ --out-dir cleaned_images
```

---

## 🎯 Command Reference

### Global Options
- `--help`, `-h`: Show help message
- `--verbose`, `-v`: Enable verbose output
- `--recursive`, `-r`: Process directories recursively

### `extract` Command
Extract and display image metadata.

**Options:**
- `--format`, `-f`: Output format (compact, detailed, json, csv)
- `--output`, `-o`: Save to file (JSON or CSV)
- `--stats`, `-s`: Show batch statistics
- `--no-internet`: Disable GPS location lookup

### `analyze` Command
Advanced image analysis.

**Options:**
- `--quality`, `-q`: Analyze image quality
- `--faces`, `-f`: Detect faces
- `--colors`, `-c`: Extract dominant colors
- `--privacy`, `-p`: Assess privacy risks
- `--all`, `-a`: Run all analyses

### `duplicates` Command
Find duplicate or similar images.

### `privacy-scan` Command
Comprehensive privacy risk scanning.

**Options:**
- `--report`: Export report to JSON file

### `stats` Command
Generate batch statistics.

**Options:**
- `--export`, `-e`: Export statistics to JSON

### `compare` Command
Compare metadata between multiple images.

### `strip` Command
Remove EXIF metadata from images.

**Options:**
- `--out-dir`, `-d`: Output directory (default: stripped_images)

---

## 📊 Output Examples

### Compact View
```
📁 IMG_1234.jpg
1920x1080 | JPEG | 2.3 MB

📍 Location: (San Francisco, California, United States)
   Lat/Lon: 37.77493, -122.41942
   View on Google Maps

📷 Apple iPhone 14 Pro
   ISO 100 | f/1.78 | 1/120s | 6.86mm
```

### Quality Analysis
```
📊 Quality Metrics
Overall Score    87.5/100
Sharpness        92.3
Brightness       128.5
Contrast         45.2
Blur Status      Sharp ✓
```

### Privacy Assessment
```
🔒 Privacy Assessment
Risk Level: HIGH
Risk Score: 65/100

Risks Found:
  • GPS location data present
  • Human-readable location name
  • Original timestamp present
  • Camera information present
```

---

## 🛠️ Advanced Usage

### Scripting & Automation

```bash
#!/bin/bash
# Process all images in a directory and generate reports

# Extract metadata
python ExifEye.py extract photos/ --recursive --output metadata.json

# Analyze quality
python ExifEye.py analyze photos/ --recursive --quality

# Find duplicates
python ExifEye.py duplicates photos/ --recursive

# Privacy scan
python ExifEye.py privacy-scan photos/ --recursive --report privacy.json

# Strip sensitive metadata
python ExifEye.py strip photos/ --recursive --out-dir cleaned/
```
---

## 🔧 Troubleshooting

### OpenCV Not Available
If you see "OpenCV not available" warnings:
```bash
pip install opencv-python numpy
```

### Face Detection Not Working
Make sure OpenCV Haar Cascade files are available:
```bash
pip install --upgrade opencv-python
```

### Permission Errors
On Linux/Mac, make the script executable:
```bash
chmod +x ExifEye.py
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Amirprx3**
- GitHub: [@Amirprx3](https://github.com/Amirprx3)

---

## 🙏 Acknowledgments

- ExifRead library for EXIF parsing
- Rich library for beautiful terminal output
- OpenCV for advanced image processing
- BigDataCloud for reverse geocoding API

---

## 📚 Resources

- [Privacy Best Practices](https://www.eff.org/issues/privacy)
- [Image Metadata Guide](https://en.wikipedia.org/wiki/Exif)

---

## ⭐ Star History

If you find this tool useful, please consider giving it a star! ⭐

---

**Made with by Amirprx3**