import re

shores = re.compile(
    r'<path[^>]+d="[^"]*m\s*(-?\d+),(-?\d+)\s+('
    r'-?(33|34),-?(33|34)|'
    r'-?(33|34),(33|34)|'
    r'(33|34),-?(33|34)|'
    r'(33|34),(33|34))[^"]*"[^>]*>'
)

def process_svg_file():
    """
    Process the image_processed.svg file to fill elements with stroke:#fb0505
    with fill:#fb0505, change shores pattern matches to color #202124,
    then change #202124 to white and red to black
    """
    
    # Read the input SVG file
    with open('image_processed.svg', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Pattern to find elements with stroke:#fb0505 and fill:none
    # This will match the style attribute and replace fill:none with fill:#fb0505
    pattern = r'(style="[^"]*fill:none[^"]*stroke:#fb0505[^"]*")'
    
    def replace_fill(match):
        style_attr = match.group(1)
        # Replace fill:none with fill:#fb0505
        new_style = style_attr.replace('fill:none', 'fill:#fb0505')
        return new_style
    
    # Apply the replacement for fill
    modified_content = re.sub(pattern, replace_fill, content)
    
    # Function to change shores color to #202124
    def change_shores_color(match):
        path_element = match.group(0)
        
        # Check if the path has a style attribute
        if 'style=' in path_element:
            # Replace any existing stroke color with #202124
            if 'stroke:' in path_element:
                # Replace existing stroke color
                path_element = re.sub(r'stroke:#[0-9a-fA-F]{6}', 'stroke:#202124', path_element)
                path_element = re.sub(r'stroke:#[0-9a-fA-F]{3}', 'stroke:#202124', path_element)
            else:
                # Add stroke color if it doesn't exist
                path_element = re.sub(r'(style="[^"]*)"', r'\1;stroke:#202124"', path_element)
        else:
            # Add style attribute with stroke color
            path_element = re.sub(r'(<path[^>]*>)', r'\1 style="stroke:#202124"', path_element)
        
        return path_element
    
    # Apply the shores color change
    modified_content = shores.sub(change_shores_color, modified_content)
    
    # Final color transformations: #202124 to black, red to red
    # Change all #202124 to black (for squares)
    modified_content = modified_content.replace('#202124', '#000000')
    
    # Change all #fb0505 (red) to red (for background)
    modified_content = modified_content.replace('#fb0505', '#ff0000')
    
    # Write the modified content to the output file
    with open('squares_filled.svg', 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Processing complete! squares_filled.svg has been created.")
    print("All elements with stroke:#fb0505 now have fill:#fb0505")
    print("All shores matching the pattern now have stroke color #202124")
    print("All #202124 colors changed to black (squares)")
    print("All red (#fb0505) colors changed to red (background)")

if __name__ == "__main__":
    process_svg_file()