#!/usr/bin/env python3

import typer
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageStat
import exifread
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import track, Progress, SpinnerColumn, TextColumn, BarColumn
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
import textwrap
from collections import Counter
from datetime import datetime
import hashlib
import csv

# Try to import OpenCV (optional)
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Note: OpenCV not available. Advanced features disabled. Install with: pip install opencv-python numpy")

# Initialize Rich Console for beautiful outputs
console = Console()

def display_banner():
    """Displays the application banner and author information."""

    logo_text = textwrap.dedent("""
███████╗██╗  ██╗██╗███████╗███████╗██╗   ██╗███████╗
██╔════╝╚██╗██╔╝██║██╔════╝██╔════╝╚██╗ ██╔╝██╔════╝
█████╗   ╚███╔╝ ██║█████╗  █████╗   ╚████╔╝ █████╗  
██╔══╝   ██╔██╗ ██║██╔══╝  ██╔══╝    ╚██╔╝  ██╔══╝  
███████╗██╔╝ ██╗██║██║     ███████╗   ██║   ███████╗
╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝
    """)

    logo = Text(logo_text, style="bold bright_cyan")

    author_info = Text.assemble(
        ("Made by ", "white"),
        ("Amirprx3", "bold bright_magenta"),
        ("\nGitHub: ", "white"),
        ("https://github.com/Amirprx3", "cyan link https://github.com/Amirprx3"),
        ("\nAn advanced tool for exploring the world of photos", "dim yellow")
    )

    console.print()
    console.print(Panel.fit(logo, border_style="magenta", title="[bold]ExifEye Pro[/bold]", padding=(1, 4)))
    console.print(Panel.fit(author_info, title="Author", border_style="dim blue", padding=(0, 4)))
    console.print()


class AdvancedImageAnalyzer:
    """Advanced image analysis features"""
    
    def __init__(self):
        self.face_cascade = None
        if OPENCV_AVAILABLE:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
            except:
                pass
    
    def analyze_quality(self, image_path: Path) -> Dict:
        """Analyze image quality metrics"""
        if not OPENCV_AVAILABLE:
            return {}
        
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {}
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(100, laplacian_var / 10)
            
            # Brightness
            brightness = np.mean(gray)
            
            # Contrast
            contrast = gray.std()
            
            # Blur detection
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_blurry = blur_score < 100
            
            # Color analysis
            pil_img = Image.open(image_path)
            stat = ImageStat.Stat(pil_img)
            
            # Overall quality score
            quality_score = (
                (sharpness_score * 0.4) +
                (min(100, contrast * 2) * 0.3) +
                (100 - abs(brightness - 128) * 0.3)
            )
            
            return {
                "quality_score": round(quality_score, 2),
                "sharpness": round(sharpness_score, 2),
                "brightness": round(brightness, 2),
                "contrast": round(contrast, 2),
                "is_blurry": is_blurry,
                "blur_metric": round(blur_score, 2),
                "color_mean": [round(x, 2) for x in stat.mean[:3]] if len(stat.mean) >= 3 else [],
                "color_stddev": [round(x, 2) for x in stat.stddev[:3]] if len(stat.stddev) >= 3 else []
            }
        except Exception as e:
            console.print(f"[dim red]Error analyzing quality for {image_path.name}: {e}[/dim red]")
            return {}
    
    def detect_faces(self, image_path: Path) -> Dict:
        """Detect faces in image"""
        if not OPENCV_AVAILABLE or not self.face_cascade:
            return {"error": "Face detection not available"}
        
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {}
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return {
                "faces_detected": len(faces),
                "face_locations": [
                    {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
                    for (x, y, w, h) in faces
                ]
            }
        except Exception as e:
            console.print(f"[dim red]Error detecting faces: {e}[/dim red]")
            return {}
    
    def extract_dominant_colors(self, image_path: Path, n_colors: int = 5) -> List[Dict]:
        """Extract dominant colors from image"""
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            img = img.resize((150, 150))
            
            pixels = list(img.getdata())
            
            # Quantize colors
            quantized = []
            for r, g, b in pixels:
                quantized.append((
                    (r // 32) * 32,
                    (g // 32) * 32,
                    (b // 32) * 32
                ))
            
            color_counts = Counter(quantized)
            dominant = color_counts.most_common(n_colors)
            
            return [
                {
                    "rgb": color,
                    "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                    "percentage": round((count / len(pixels)) * 100, 2)
                }
                for color, count in dominant
            ]
        except Exception as e:
            console.print(f"[dim red]Error extracting colors: {e}[/dim red]")
            return []
    
    def calculate_perceptual_hash(self, image_path: Path) -> Optional[str]:
        """Calculate perceptual hash for duplicate detection"""
        try:
            img = Image.open(image_path)
            img = img.convert('L').resize((32, 32), Image.Resampling.LANCZOS)
            pixels = list(img.getdata())
            avg = sum(pixels) / len(pixels)
            bits = ''.join('1' if p > avg else '0' for p in pixels)
            return hex(int(bits, 2))[2:].zfill(16)
        except Exception as e:
            return None
    
    def analyze_privacy_risk(self, metadata: Dict) -> Dict:
        """Analyze privacy risks in image metadata"""
        risk_score = 0
        risks = []
        
        if metadata.get('gps_info'):
            risk_score += 40
            risks.append("GPS location data present")
            if 'location_name' in metadata['gps_info']:
                risk_score += 10
                risks.append("Human-readable location name")
        
        if metadata.get('additional_info', {}).get('date_time_original') != 'N/A':
            risk_score += 10
            risks.append("Original timestamp present")
        
        camera_info = metadata.get('camera_info', {})
        if camera_info.get('make') != 'N/A' or camera_info.get('model') != 'N/A':
            risk_score += 10
            risks.append("Camera information present")
        
        additional = metadata.get('additional_info', {})
        if additional.get('copyright') != 'N/A':
            risk_score += 5
            risks.append("Copyright information")
        if additional.get('software') != 'N/A':
            risk_score += 5
            risks.append("Software information")
        
        if risk_score >= 50:
            level = "HIGH"
            color = "red"
        elif risk_score >= 30:
            level = "MEDIUM"
            color = "yellow"
        else:
            level = "LOW"
            color = "green"
        
        return {
            "risk_score": min(100, risk_score),
            "risk_level": level,
            "risk_color": color,
            "risks_found": risks
        }


class ImageMetadataExtractor:
    """
    A professional class to extract, display, and manage image metadata.
    """

    def __init__(self, no_internet: bool = False, verbose: bool = False):
        self.no_internet = no_internet
        self.verbose = verbose

    def _log(self, message: str):
        """Logs an internal message if verbose mode is on."""
        if self.verbose:
            rprint(f"[dim i]INFO: {message}[/dim i]")

    def _convert_to_degrees(self, value) -> Optional[float]:
        """Converts GPS coordinates from DMS (Degrees, Minutes, Seconds) to DD (Decimal Degrees)."""
        try:
            d = float(value.values[0].num) / float(value.values[0].den)
            m = float(value.values[1].num) / float(value.values[1].den)
            s = float(value.values[2].num) / float(value.values[2].den)
            return d + (m / 60.0) + (s / 3600.0)
        except (AttributeError, ZeroDivisionError, IndexError):
            return None

    def _get_location_name(self, lat: float, lon: float) -> Optional[str]:
        """Fetches a human-readable location name using a reverse geocoding service."""
        if self.no_internet:
            self._log("Internet lookup is disabled.")
            return None
        try:
            self._log(f"Looking up location for coordinates: {lat:.6f}, {lon:.6f}")
            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            parts = [data.get(key) for key in ['city', 'principalSubdivision', 'countryName']]
            location_name = ', '.join(filter(None, parts))
            self._log(f"Location found: {location_name}")
            return location_name if location_name else "Unknown Location"
        except requests.RequestException as e:
            self._log(f"Could not get location name: {e}")
            return None

    def extract_metadata(self, image_path: Path) -> Optional[Dict]:
        """Extracts comprehensive metadata from a single image file."""
        if not image_path.is_file():
            console.print(f"[bold red]Error: File '{image_path}' does not exist.[/bold red]")
            return None
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=True)
                f.seek(0)
                with Image.open(f) as img:
                    img_info = {
                        "format": img.format, "mode": img.mode, "dimensions": f"{img.width}x{img.height}",
                    }
        except Exception as e:
            console.print(f"[bold red]Error processing image '{image_path}': {e}[/bold red]")
            return None

        gps_info = {}
        if (gps_lat_tag := tags.get('GPS GPSLatitude')) and \
           (gps_lon_tag := tags.get('GPS GPSLongitude')) and \
           (gps_lat_ref := tags.get('GPS GPSLatitudeRef')) and \
           (gps_lon_ref := tags.get('GPS GPSLongitudeRef')):
            lat = self._convert_to_degrees(gps_lat_tag)
            lon = self._convert_to_degrees(gps_lon_tag)
            if lat is not None and lon is not None:
                if str(gps_lat_ref.values) != 'N': lat = -lat
                if str(gps_lon_ref.values) != 'E': lon = -lon
                gps_info = {"latitude": lat, "longitude": lon, "Maps_link": f"https://www.google.com/maps?q={lat},{lon}"}
                if location_name := self._get_location_name(lat, lon):
                    gps_info["location_name"] = location_name

        metadata = {
            "file_info": {"filename": image_path.name, "filepath": str(image_path.resolve()), "file_size": image_path.stat().st_size, **img_info},
            "gps_info": gps_info or None,
            "camera_info": {"make": str(tags.get('Image Make', 'N/A')), "model": str(tags.get('Image Model', 'N/A')), "iso": str(tags.get('EXIF ISOSpeedRatings', 'N/A')), "focal_length": str(tags.get('EXIF FocalLength', 'N/A')), "aperture": str(tags.get('EXIF FNumber', 'N/A')), "shutter_speed": str(tags.get('EXIF ExposureTime', 'N/A'))},
            "additional_info": {"date_time_original": str(tags.get('EXIF DateTimeOriginal', 'N/A')), "software": str(tags.get('Image Software', 'N/A')), "copyright": str(tags.get('Image Copyright', 'N/A'))},
        }
        return metadata

    @staticmethod
    def strip_metadata(source_path: Path, dest_path: Path):
        """Removes all EXIF metadata from an image and saves it to a new file."""
        try:
            with Image.open(source_path) as img:
                img_data = list(img.getdata())
                img_no_exif = Image.new(img.mode, img.size)
                img_no_exif.putdata(img_data)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                img_no_exif.save(dest_path, format=img.format)
            return True
        except Exception as e:
            console.print(f"[bold red]Error stripping metadata from '{source_path}': {e}[/bold red]")
            return False


class BatchAnalyzer:
    """Batch analysis and statistics"""
    
    @staticmethod
    def generate_statistics(all_metadata: List[Dict]) -> Dict:
        """Generate comprehensive statistics from multiple images"""
        stats = {
            "total_images": len(all_metadata),
            "with_gps": 0,
            "with_camera_info": 0,
            "locations": [],
            "cameras": [],
            "dates": [],
            "total_size_mb": 0
        }
        
        for meta in all_metadata:
            if meta.get('gps_info'):
                stats["with_gps"] += 1
                if loc := meta['gps_info'].get('location_name'):
                    stats["locations"].append(loc)
            
            camera = meta.get('camera_info', {})
            if camera.get('make') != 'N/A':
                stats["with_camera_info"] += 1
                camera_name = f"{camera.get('make')} {camera.get('model')}"
                stats["cameras"].append(camera_name)
            
            if date := meta.get('additional_info', {}).get('date_time_original'):
                if date != 'N/A':
                    stats["dates"].append(date)
            
            stats["total_size_mb"] += meta.get('file_info', {}).get('file_size', 0)
        
        stats["total_size_mb"] = round(stats["total_size_mb"] / (1024 * 1024), 2)
        
        if stats["locations"]:
            stats["most_common_location"] = Counter(stats["locations"]).most_common(1)[0]
        if stats["cameras"]:
            stats["most_common_camera"] = Counter(stats["cameras"]).most_common(1)[0]
        
        return stats
    
    @staticmethod
    def display_statistics(stats: Dict):
        """Display statistics in a beautiful table"""
        table = Table(title="📊 Batch Analysis Statistics", show_header=False, border_style="cyan")
        table.add_column("Metric", style="cyan bold")
        table.add_column("Value", style="green")
        
        table.add_row("Total Images", str(stats["total_images"]))
        table.add_row("Images with GPS", f"{stats['with_gps']} ({stats['with_gps']/max(1, stats['total_images'])*100:.1f}%)")
        table.add_row("Images with Camera Info", str(stats["with_camera_info"]))
        table.add_row("Total Size", f"{stats['total_size_mb']} MB")
        
        if most_loc := stats.get("most_common_location"):
            table.add_row("Most Common Location", f"{most_loc[0]} ({most_loc[1]} images)")
        
        if most_cam := stats.get("most_common_camera"):
            table.add_row("Most Common Camera", f"{most_cam[0]} ({most_cam[1]} images)")
        
        console.print("\n")
        console.print(table)
        console.print("\n")
    
    @staticmethod
    def find_duplicates(all_metadata: List[Dict]) -> List[List[str]]:
        """Find duplicate images using perceptual hashing"""
        analyzer = AdvancedImageAnalyzer()
        hashes = {}
        
        for meta in all_metadata:
            filepath = meta['file_info']['filepath']
            phash = analyzer.calculate_perceptual_hash(Path(filepath))
            if phash:
                if phash not in hashes:
                    hashes[phash] = []
                hashes[phash].append(filepath)
        
        duplicates = [files for files in hashes.values() if len(files) > 1]
        return duplicates


# --- Output Display Functions ---

def display_compact(metadata: Dict):
    """Displays metadata in a compact, user-friendly panel."""
    file_info, gps_info, camera_info = metadata['file_info'], metadata['gps_info'], metadata['camera_info']

    panel_content = f"[bold cyan]📁 {file_info['filename']}[/bold cyan]\n[dim]{file_info['dimensions']} | {file_info['format']} | {file_info['file_size'] / 1024:.1f} KB[/dim]\n"

    if gps_info:
        loc_name = f" ([cyan]{gps_info.get('location_name', '')}[/cyan])" if 'location_name' in gps_info else ""
        panel_content += f"\n[bold green]📍 Location:{loc_name}[/bold green]\n   Lat/Lon: {gps_info['latitude']:.5f}, {gps_info['longitude']:.5f}\n   [link={gps_info['Maps_link']}]View on Google Maps[/link]"
    else:
        panel_content += "\n[yellow]📍 No GPS information available.[/yellow]"

    if camera_info.get('make') != 'N/A':
        panel_content += f"\n\n[bold yellow]📷 {camera_info['make']} {camera_info['model']}[/bold yellow]\n   [dim]ISO {camera_info['iso']} | f/{camera_info['aperture']} | {camera_info['shutter_speed']}s | {camera_info['focal_length']}mm[/dim]"

    console.print(Panel(panel_content, expand=False, border_style="dim"))

def display_detailed(metadata: Dict):
    """Displays metadata in detailed, separate tables."""
    rprint(f"\n[bold underline]Detailed Metadata for: {metadata['file_info']['filename']}[/bold underline]")
    def create_table(title: str, data: Dict):
        table = Table(title=title, show_header=False, box=None, title_style="bold magenta")
        table.add_column("Key", style="cyan"); table.add_column("Value", style="white")
        for key, value in data.items():
            if value: table.add_row(key.replace('_', ' ').title(), str(value))
        return table

    console.print(create_table("File Information", metadata['file_info']))
    if metadata['gps_info']: console.print(create_table("GPS Information", metadata['gps_info']))
    if metadata['camera_info']: console.print(create_table("Camera Information", metadata['camera_info']))
    if metadata['additional_info']: console.print(create_table("Additional Information", metadata['additional_info']))
    console.print("---" * 20, style="dim")

def display_advanced_analysis(image_path: Path, metadata: Dict, show_quality: bool, show_faces: bool, show_colors: bool, show_privacy: bool):
    """Display advanced analysis results"""
    analyzer = AdvancedImageAnalyzer()
    
    rprint(f"\n[bold bright_cyan]🔍 Advanced Analysis: {image_path.name}[/bold bright_cyan]")
    
    # Quality analysis
    if show_quality and OPENCV_AVAILABLE:
        quality = analyzer.analyze_quality(image_path)
        if quality:
            quality_table = Table(title="📊 Quality Metrics", show_header=False, border_style="blue")
            quality_table.add_column("Metric", style="cyan")
            quality_table.add_column("Value", style="green")
            
            quality_table.add_row("Overall Score", f"{quality['quality_score']:.1f}/100")
            quality_table.add_row("Sharpness", f"{quality['sharpness']:.1f}")
            quality_table.add_row("Brightness", f"{quality['brightness']:.1f}")
            quality_table.add_row("Contrast", f"{quality['contrast']:.1f}")
            quality_table.add_row("Blur Status", "Blurry ⚠️" if quality['is_blurry'] else "Sharp ✓")
            
            console.print(quality_table)
    
    # Face detection
    if show_faces and OPENCV_AVAILABLE:
        faces = analyzer.detect_faces(image_path)
        if 'faces_detected' in faces:
            face_emoji = "👤" if faces['faces_detected'] == 1 else "👥"
            rprint(f"\n{face_emoji} [magenta]Faces Detected:[/magenta] [bold]{faces['faces_detected']}[/bold]")
    
    # Dominant colors
    if show_colors:
        colors = analyzer.extract_dominant_colors(image_path, 5)
        if colors:
            color_table = Table(title="🎨 Dominant Colors", show_header=True, border_style="magenta")
            color_table.add_column("#", style="dim", width=3)
            color_table.add_column("Color", width=10)
            color_table.add_column("Hex", style="cyan")
            color_table.add_column("Percentage", style="green")
            
            for i, color_info in enumerate(colors, 1):
                color_box = f"[on {color_info['hex']}]    [/on {color_info['hex']}]"
                color_table.add_row(str(i), color_box, color_info['hex'], f"{color_info['percentage']:.1f}%")
            
            console.print("\n")
            console.print(color_table)
    
    # Privacy risk
    if show_privacy:
        privacy = analyzer.analyze_privacy_risk(metadata)
        
        privacy_panel_content = f"[bold {privacy['risk_color']}]Risk Level: {privacy['risk_level']}[/bold {privacy['risk_color']}]\n"
        privacy_panel_content += f"Risk Score: {privacy['risk_score']}/100\n\n"
        
        if privacy['risks_found']:
            privacy_panel_content += "[bold]Risks Found:[/bold]\n"
            for risk in privacy['risks_found']:
                privacy_panel_content += f"  • {risk}\n"
        else:
            privacy_panel_content += "[green]No privacy risks detected[/green]"
        
        console.print("\n")
        console.print(Panel(privacy_panel_content, title="🔒 Privacy Assessment", border_style=privacy['risk_color']))
    
    console.print("\n" + "─" * 80 + "\n")

# --- File Saving Functions ---

def save_to_file(data: list, output_file: Path, file_format: str):
    """Saves data to a file in the specified format (JSON or CSV)."""
    try:
        if file_format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif file_format == 'csv':
            if not data: return
            flat_data = []
            for item in data:
                row = {
                    **(item.get('file_info') or {}),  # Add or {} for handle none
                    **(item.get('gps_info') or {}),
                    **(item.get('camera_info') or {}),
                    **(item.get('additional_info') or {})
                }
                flat_data.append(row)

            if not flat_data: 
                console.print("[red]No data to write to CSV.[/red]")
                return
            
            headers = list(flat_data[0].keys())

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(flat_data)

        console.print(f"[green]✔ Successfully saved metadata to '{output_file}'[/green]")
    except Exception as e:
        console.print(f"[bold red]Error saving to {output_file.name}: {e}[/bold red]")

# --- Main CLI Application with Typer ---

app = typer.Typer(
    name="exifeye",
    help="👁️  ExifEye Pro: Professional Image Metadata Extractor & Analyzer with Advanced Features.",
    add_completion=False,
    rich_markup_mode="rich"
)

def get_image_files(paths: List[Path], recursive: bool) -> List[Path]:
    """Collects all valid image files from the given paths."""
    image_files = []
    supported_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
    for path in paths:
        if path.is_file() and path.suffix.lower() in supported_extensions:
            image_files.append(path)
        elif path.is_dir():
            pattern = '**/*' if recursive else '*'
            for file_path in path.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    image_files.append(file_path)
    return list(sorted(set(image_files)))


@app.command(name="extract", help="Extract and display metadata from images.")
def extract_cli(
    images: List[Path] = typer.Argument(..., help="Path to image file(s) or directory(ies).", exists=True),
    output_format: str = typer.Option("compact", "--format", "-f", help="Output format: compact, detailed, json, or csv."),
    output_file: Path = typer.Option(None, "--output", "-o", help="Output file path (for json or csv)."),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Process directories recursively."),
    no_internet: bool = typer.Option(False, "--no-internet", help="Disable internet-based location lookup."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output for debugging."),
    stats: bool = typer.Option(False, "--stats", "-s", help="Show batch statistics.")
):
    """The command to extract metadata."""
    if not output_file and sys.stdout.isatty():
        display_banner()

    image_files = get_image_files(images, recursive)
    if not image_files:
        rprint("[bold red]No image files found to process.[/bold red]"); raise typer.Exit(1)

    extractor = ImageMetadataExtractor(no_internet=no_internet, verbose=verbose)
    all_metadata = []

    for image_path in track(image_files, description="[cyan]Analyzing images...[/cyan]"):
        metadata = extractor.extract_metadata(image_path)
        if metadata:
            all_metadata.append(metadata)

    if output_file:
        file_format = output_file.suffix.lower().strip('.')
        if file_format not in ['json', 'csv']:
            rprint("[bold red]Error: Output file must have a .json or .csv extension.[/bold red]"); raise typer.Exit(1)
        save_to_file(all_metadata, output_file, file_format)
    else:
        if not all_metadata:
            rprint("[bold yellow]No metadata could be extracted.[/bold yellow]"); return

        rprint(f"\n[bold green]✅ Analysis complete. Found metadata in {len(all_metadata)} of {len(image_files)} images.[/bold green]\n")

        if stats:
            batch_stats = BatchAnalyzer.generate_statistics(all_metadata)
            BatchAnalyzer.display_statistics(batch_stats)

        if output_format == "compact":
            for metadata in all_metadata: display_compact(metadata)
        elif output_format == "detailed":
            for metadata in all_metadata: display_detailed(metadata)
        elif output_format == "json":
            console.print_json(data=all_metadata)
        elif output_format == "csv":
             rprint("[bold yellow]Warning: CSV output is only supported when saving to a file with the --output flag.[/bold yellow]")


@app.command(name="analyze", help="🔬 Advanced image analysis (quality, faces, colors, privacy).")
def analyze_cli(
    images: List[Path] = typer.Argument(..., help="Path to image file(s) or directory(ies).", exists=True),
    quality: bool = typer.Option(False, "--quality", "-q", help="Analyze image quality metrics."),
    faces: bool = typer.Option(False, "--faces", "-f", help="Detect faces in images."),
    colors: bool = typer.Option(False, "--colors", "-c", help="Extract dominant colors."),
    privacy: bool = typer.Option(False, "--privacy", "-p", help="Assess privacy risks."),
    all_analysis: bool = typer.Option(False, "--all", "-a", help="Run all analyses."),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Process directories recursively."),
    no_internet: bool = typer.Option(False, "--no-internet", help="Disable internet-based location lookup."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output.")
):
    """Advanced analysis command with quality, face detection, color extraction, and privacy assessment."""
    
    if not OPENCV_AVAILABLE and (quality or faces or all_analysis):
        rprint("[bold red]Error: OpenCV is required for quality and face detection features.[/bold red]")
        rprint("Install with: [cyan]pip install opencv-python numpy[/cyan]")
        raise typer.Exit(1)
    
    display_banner()
    
    # If --all is set, enable all analyses
    if all_analysis:
        quality = faces = colors = privacy = True
    
    # If no specific analysis is requested, show all by default
    if not (quality or faces or colors or privacy):
        quality = faces = colors = privacy = True
    
    image_files = get_image_files(images, recursive)
    if not image_files:
        rprint("[bold red]No image files found to process.[/bold red]")
        raise typer.Exit(1)
    
    extractor = ImageMetadataExtractor(no_internet=no_internet, verbose=verbose)
    
    rprint(f"[bold green]Found {len(image_files)} image(s) to analyze.[/bold green]\n")
    
    for image_path in image_files:
        metadata = extractor.extract_metadata(image_path)
        if metadata:
            display_advanced_analysis(
                image_path, 
                metadata, 
                show_quality=quality,
                show_faces=faces,
                show_colors=colors,
                show_privacy=privacy
            )


@app.command(name="duplicates", help="🔎 Find duplicate or similar images.")
def duplicates_cli(
    images: List[Path] = typer.Argument(..., help="Path to image file(s) or directory(ies).", exists=True),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Process directories recursively."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output.")
):
    """Find duplicate images using perceptual hashing."""
    display_banner()
    
    image_files = get_image_files(images, recursive)
    if not image_files:
        rprint("[bold red]No image files found to process.[/bold red]")
        raise typer.Exit(1)
    
    extractor = ImageMetadataExtractor(verbose=verbose)
    all_metadata = []
    
    rprint(f"[cyan]Analyzing {len(image_files)} images for duplicates...[/cyan]\n")
    
    for image_path in track(image_files, description="[cyan]Calculating hashes...[/cyan]"):
        metadata = extractor.extract_metadata(image_path)
        if metadata:
            all_metadata.append(metadata)
    
    duplicates = BatchAnalyzer.find_duplicates(all_metadata)
    
    if duplicates:
        rprint(f"\n[bold yellow]⚠️  Found {len(duplicates)} group(s) of duplicate images:[/bold yellow]\n")
        
        for i, group in enumerate(duplicates, 1):
            panel_content = ""
            for filepath in group:
                panel_content += f"  • {Path(filepath).name}\n"
                if verbose:
                    panel_content += f"    [dim]{filepath}[/dim]\n"
            
            console.print(Panel(
                panel_content.strip(),
                title=f"Duplicate Group {i}",
                border_style="yellow"
            ))
            console.print()
    else:
        rprint("[bold green]✅ No duplicate images found![/bold green]")


@app.command(name="strip", help="🧹 Remove all EXIF metadata from images.")
def strip_cli(
    images: List[Path] = typer.Argument(..., help="Path to image file(s) or directory(ies).", exists=True),
    output_dir: Path = typer.Option("stripped_images", "--out-dir", "-d", help="Directory to save modified images."),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Process directories recursively.")
):
    """The command to strip metadata for privacy."""
    if sys.stdout.isatty():
        display_banner()

    image_files = get_image_files(images, recursive)
    if not image_files:
        rprint("[bold red]No image files found to process.[/bold red]"); raise typer.Exit(1)

    output_dir.mkdir(exist_ok=True, parents=True)

    success_count = 0
    for image_path in track(image_files, description="[cyan]Stripping metadata...[/cyan]"):
        dest_path = output_dir / image_path.name
        if ImageMetadataExtractor.strip_metadata(image_path, dest_path):
            success_count += 1

    rprint(f"\n[bold green]✨ Finished! Stripped metadata from {success_count}/{len(image_files)} images.[/bold green]")
    rprint(f"Cleaned images are saved in: [cyan]'{output_dir.resolve()}'[/cyan]")


@app.command(name="stats", help="📊 Generate comprehensive statistics from multiple images.")
def stats_cli(
    images: List[Path] = typer.Argument(..., help="Path to image file(s) or directory(ies).", exists=True),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Process directories recursively."),
    no_internet: bool = typer.Option(False, "--no-internet", help="Disable internet-based location lookup."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    export: Optional[Path] = typer.Option(None, "--export", "-e", help="Export statistics to JSON file.")
):
    """Generate and display batch statistics."""
    display_banner()
    
    image_files = get_image_files(images, recursive)
    if not image_files:
        rprint("[bold red]No image files found to process.[/bold red]")
        raise typer.Exit(1)
    
    extractor = ImageMetadataExtractor(no_internet=no_internet, verbose=verbose)
    all_metadata = []
    
    for image_path in track(image_files, description="[cyan]Analyzing images...[/cyan]"):
        metadata = extractor.extract_metadata(image_path)
        if metadata:
            all_metadata.append(metadata)
    
    if not all_metadata:
        rprint("[bold yellow]No metadata could be extracted.[/bold yellow]")
        return
    
    stats = BatchAnalyzer.generate_statistics(all_metadata)
    BatchAnalyzer.display_statistics(stats)
    
    # Additional detailed statistics
    if stats.get("locations"):
        location_counts = Counter(stats["locations"])
        if len(location_counts) > 1:
            rprint("[bold cyan]📍 Top Locations:[/bold cyan]")
            for location, count in location_counts.most_common(5):
                rprint(f"  • {location}: {count} images")
            rprint()
    
    if stats.get("cameras"):
        camera_counts = Counter(stats["cameras"])
        if len(camera_counts) > 1:
            rprint("[bold cyan]📷 Camera Usage:[/bold cyan]")
            for camera, count in camera_counts.most_common(5):
                rprint(f"  • {camera}: {count} images")
            rprint()
    
    if export:
        try:
            with open(export, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            rprint(f"[green]✔ Statistics exported to '{export}'[/green]")
        except Exception as e:
            rprint(f"[red]Error exporting statistics: {e}[/red]")


@app.command(name="compare", help="⚖️  Compare metadata between multiple images.")
def compare_cli(
    images: List[Path] = typer.Argument(..., help="Path to 2 or more image files to compare.", exists=True),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output.")
):
    """Compare metadata between multiple images."""
    display_banner()
    
    if len(images) < 2:
        rprint("[bold red]Error: Please provide at least 2 images to compare.[/bold red]")
        raise typer.Exit(1)
    
    extractor = ImageMetadataExtractor(verbose=verbose)
    all_metadata = []
    
    for image_path in images:
        if not image_path.is_file():
            rprint(f"[yellow]Warning: Skipping '{image_path}' (not a file)[/yellow]")
            continue
        
        metadata = extractor.extract_metadata(image_path)
        if metadata:
            all_metadata.append(metadata)
    
    if len(all_metadata) < 2:
        rprint("[bold red]Error: Could not extract metadata from enough images.[/bold red]")
        raise typer.Exit(1)
    
    # Create comparison table
    comparison_table = Table(title="📋 Image Comparison", show_header=True, border_style="cyan")
    comparison_table.add_column("Property", style="cyan bold")
    
    for meta in all_metadata:
        comparison_table.add_column(meta['file_info']['filename'][:20], style="white")
    
    # Compare dimensions
    dimensions = [meta['file_info']['dimensions'] for meta in all_metadata]
    comparison_table.add_row("Dimensions", *dimensions)
    
    # Compare format
    formats = [meta['file_info']['format'] for meta in all_metadata]
    comparison_table.add_row("Format", *formats)
    
    # Compare size
    sizes = [f"{meta['file_info']['file_size'] / 1024:.1f} KB" for meta in all_metadata]
    comparison_table.add_row("File Size", *sizes)
    
    # Compare GPS
    gps_status = []
    for meta in all_metadata:
        if meta.get('gps_info'):
            loc = meta['gps_info'].get('location_name', 'Unknown')
            gps_status.append(f"✓ {loc[:15]}")
        else:
            gps_status.append("✗ No GPS")
    comparison_table.add_row("GPS Location", *gps_status)
    
    # Compare camera
    cameras = []
    for meta in all_metadata:
        camera = meta.get('camera_info', {})
        if camera.get('make') != 'N/A':
            cameras.append(f"{camera.get('make')} {camera.get('model')}"[:20])
        else:
            cameras.append("N/A")
    comparison_table.add_row("Camera", *cameras)
    
    # Compare date
    dates = []
    for meta in all_metadata:
        date = meta.get('additional_info', {}).get('date_time_original', 'N/A')
        dates.append(date if date != 'N/A' else 'N/A')
    comparison_table.add_row("Date Taken", *dates)
    
    console.print("\n")
    console.print(comparison_table)
    console.print("\n")


@app.command(name="privacy-scan", help="🔒 Scan images for privacy risks and generate report.")
def privacy_scan_cli(
    images: List[Path] = typer.Argument(..., help="Path to image file(s) or directory(ies).", exists=True),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Process directories recursively."),
    no_internet: bool = typer.Option(False, "--no-internet", help="Disable internet-based location lookup."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    report: Optional[Path] = typer.Option(None, "--report", help="Export privacy report to JSON file.")
):
    """Scan all images for privacy risks and generate a comprehensive report."""
    display_banner()
    
    image_files = get_image_files(images, recursive)
    if not image_files:
        rprint("[bold red]No image files found to process.[/bold red]")
        raise typer.Exit(1)
    
    extractor = ImageMetadataExtractor(no_internet=no_internet, verbose=verbose)
    analyzer = AdvancedImageAnalyzer()
    
    high_risk = []
    medium_risk = []
    low_risk = []
    
    rprint(f"[cyan]Scanning {len(image_files)} images for privacy risks...[/cyan]\n")
    
    for image_path in track(image_files, description="[cyan]Analyzing privacy...[/cyan]"):
        metadata = extractor.extract_metadata(image_path)
        if metadata:
            privacy = analyzer.analyze_privacy_risk(metadata)
            
            result = {
                "filename": metadata['file_info']['filename'],
                "filepath": metadata['file_info']['filepath'],
                "risk_level": privacy['risk_level'],
                "risk_score": privacy['risk_score'],
                "risks": privacy['risks_found']
            }
            
            if privacy['risk_level'] == "HIGH":
                high_risk.append(result)
            elif privacy['risk_level'] == "MEDIUM":
                medium_risk.append(result)
            else:
                low_risk.append(result)
    
    # Display summary
    summary_table = Table(title="🔒 Privacy Scan Summary", show_header=True, border_style="cyan")
    summary_table.add_column("Risk Level", style="bold")
    summary_table.add_column("Count", style="white")
    summary_table.add_column("Percentage", style="white")
    
    total = len(image_files)
    summary_table.add_row("[red]HIGH RISK[/red]", str(len(high_risk)), f"{len(high_risk)/total*100:.1f}%")
    summary_table.add_row("[yellow]MEDIUM RISK[/yellow]", str(len(medium_risk)), f"{len(medium_risk)/total*100:.1f}%")
    summary_table.add_row("[green]LOW RISK[/green]", str(len(low_risk)), f"{len(low_risk)/total*100:.1f}%")
    
    console.print("\n")
    console.print(summary_table)
    console.print("\n")
    
    # Show high-risk images
    if high_risk:
        rprint("[bold red]⚠️  HIGH RISK Images:[/bold red]\n")
        for item in high_risk[:10]:  # Show first 10
            rprint(f"  • [red]{item['filename']}[/red]")
            for risk in item['risks']:
                rprint(f"    - {risk}")
        if len(high_risk) > 10:
            rprint(f"\n  ... and {len(high_risk) - 10} more")
        rprint()
    
    # Export report
    if report:
        report_data = {
            "scan_date": datetime.now().isoformat(),
            "total_images": total,
            "summary": {
                "high_risk": len(high_risk),
                "medium_risk": len(medium_risk),
                "low_risk": len(low_risk)
            },
            "high_risk_images": high_risk,
            "medium_risk_images": medium_risk,
            "low_risk_images": low_risk
        }
        
        try:
            with open(report, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            rprint(f"[green]✔ Privacy report exported to '{report}'[/green]")
        except Exception as e:
            rprint(f"[red]Error exporting report: {e}[/red]")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Main callback that runs if no command is specified."""
    if ctx.invoked_subcommand is None:
        display_banner()
        rprint("Use '[bold cyan]exifeye --help[/bold cyan]' to see available commands.")
        rprint("\n[dim]Available commands:[/dim]")
        rprint("  • [cyan]extract[/cyan]       - Extract and display metadata")
        rprint("  • [cyan]analyze[/cyan]       - Advanced analysis (quality, faces, colors)")
        rprint("  • [cyan]strip[/cyan]         - Remove metadata for privacy")
        rprint("  • [cyan]stats[/cyan]         - Generate batch statistics")
        rprint("  • [cyan]duplicates[/cyan]    - Find duplicate images")
        rprint("  • [cyan]compare[/cyan]       - Compare multiple images")
        rprint("  • [cyan]privacy-scan[/cyan]  - Scan for privacy risks")
        rprint()


if __name__ == "__main__":
    app()