#!/bin/bash

# Script to split the themes screenshot into individual theme images
# Requires ImageMagick to be installed

# Source image
SOURCE=".attic/pyccsl-themes.png"

# Output directory
OUTPUT_DIR="images"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# The image appears to have 8 themes, each taking roughly the same vertical space
# Image dimensions appear to be approximately 838x1450 pixels
# Each theme section is roughly 180 pixels tall

# Define theme names in order
themes=(
    "default"
    "nord"
    "dracula"
    "solarized"
    "gruvbox"
    "tokyo"
    "catppuccin"
    "minimal"
)

# Height of each theme section (including spacing)
section_height=180

# Starting Y position (first theme starts around pixel 45)
start_y=45

# Height to crop for each theme (just the status line, not the label)
crop_height=50

# X position and width for the status line
x_pos=8
width=820

echo "Splitting themes from $SOURCE..."

for i in "${!themes[@]}"; do
    theme="${themes[$i]}"
    
    # Calculate Y position for this theme's status line
    # The status line is about 45 pixels below each "Theme:" label
    y_pos=$((start_y + (i * section_height) + 45))
    
    # Crop command: widthxheight+x+y
    crop_geometry="${width}x${crop_height}+${x_pos}+${y_pos}"
    
    output_file="${OUTPUT_DIR}/theme-${theme}.png"
    
    echo "Extracting theme: $theme (${crop_geometry}) -> $output_file"
    
    # Use ImageMagick's convert command to crop
    convert "$SOURCE" -crop "$crop_geometry" "$output_file"
done

echo "Done! Theme images saved to $OUTPUT_DIR/"

# Optional: Create a clean version without the performance badge (●○○○)
# This would crop from position 60 instead of 8 to skip the badge
echo ""
echo "Creating additional crops without performance badges..."

for i in "${!themes[@]}"; do
    theme="${themes[$i]}"
    
    # Calculate Y position for this theme's status line
    y_pos=$((start_y + (i * section_height) + 45))
    
    # Crop from x=60 to skip the performance badge
    crop_geometry="760x${crop_height}+60+${y_pos}"
    
    output_file="${OUTPUT_DIR}/theme-${theme}-no-badge.png"
    
    echo "Extracting theme without badge: $theme -> $output_file"
    
    convert "$SOURCE" -crop "$crop_geometry" "$output_file"
done

echo "All done! Check the $OUTPUT_DIR/ directory for the cropped images."