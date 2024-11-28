#!/bin/bash

# Directory containing JSON files
DATA_DIR="ui/src/data"

# Directory containing icons
ICON_DIR="ui/public/assets/icons"

# Iterate over each JSON file in the data directory
for file in "$DATA_DIR"/*.json; do
    # Extract the base name without extension (e.g., AIJasonZ from AIJasonZ.json)
    base=$(basename "$file" .json)
    
    # Define the channelIcon path
    icon_path="$ICON_DIR/${base}.jpg"
    
    # Check if the icon file exists
    if [ ! -f "public${icon_path}" ]; then
        echo "Warning: Icon for channel '$base' not found at 'public${icon_path}'. Using default icon."
        icon_path="ui/public/assets/icons/default_icon.png"
    fi
    
    # Use jq to add the channelIcon field to each JSON object
    jq --arg icon "$icon_path" '
        map(. + {channelIcon: $icon})
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
    
    echo "Updated '$file' with channelIcon: '$icon_path'"
done
