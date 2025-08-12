import re

def process_svg_colors():
    # Read the SVG file
    with open('image_processed.svg', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all hex color codes (#xxxxxx)
    hex_pattern = r'#([0-9a-fA-F]{6})'
    
    def replace_color(match):
        color = match.group(1).lower()
        # Change #0000ff to #fb0505, keep #fb0505 unchanged, replace all others with #202124
        if color == '0000ff':
            return '#fb0505'
        elif color == 'fb0505':
            return match.group(0)  # Return original match unchanged
        else:
            return '#202124'
    
    # Replace colors using the function
    processed_content = re.sub(hex_pattern, replace_color, content)
    
    # Write the processed content to a new file
    with open('image_processed_updated.svg', 'w', encoding='utf-8') as file:
        file.write(processed_content)
    
    print("SVG processing completed!")
    print("Original colors replaced with #202124 (except #fb0505)")
    print("#0000ff changed to #fb0505")
    print("Output saved to: image_processed_updated.svg")

if __name__ == "__main__":
    process_svg_colors()