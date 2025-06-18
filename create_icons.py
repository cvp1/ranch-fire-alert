#!/usr/bin/env python3
"""
Create PWA icons for Ranch Fire Alert System
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple fire alert icon"""
    # Create a new image with a red background
    img = Image.new('RGBA', (size, size), (211, 47, 47, 255))  # Red background
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions
    margin = size // 8
    center = size // 2
    
    # Draw a simple flame shape
    flame_points = [
        (center, margin),  # Top
        (center - size//6, center - size//8),  # Left
        (center - size//8, center + size//8),  # Bottom left
        (center, center + size//4),  # Bottom
        (center + size//8, center + size//8),  # Bottom right
        (center + size//6, center - size//8),  # Right
    ]
    
    # Draw the flame in orange/yellow
    draw.polygon(flame_points, fill=(255, 165, 0, 255))  # Orange flame
    
    # Add a border
    border_width = max(2, size // 64)
    draw.rectangle([0, 0, size-1, size-1], outline=(255, 255, 255, 255), width=border_width)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Create all required icons"""
    # Ensure the icons directory exists
    os.makedirs('static/icons', exist_ok=True)
    
    # Create icons
    create_icon(192, 'static/icons/icon-192.png')
    create_icon(512, 'static/icons/icon-512.png')
    
    print("All icons created successfully!")

if __name__ == '__main__':
    main() 