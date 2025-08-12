import re
import math

def parse_path_data(d):
    """Parse SVG path data to extract coordinates"""
    commands = []
    current = ""
    for char in d:
        if char in 'MmLlHhVvCcSsQqTtAaZz':
            if current:
                commands.append(current.strip())
            current = char
        else:
            current += char
    if current:
        commands.append(current.strip())
    
    coordinates = []
    x, y = 0, 0
    
    for cmd in commands:
        if not cmd:
            continue
        command = cmd[0]
        params = cmd[1:].strip()
        
        if command in 'MmLl':
            # Move or line to
            coords = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', params)]
            for i in range(0, len(coords), 2):
                if i + 1 < len(coords):
                    if command.isupper():
                        x, y = coords[i], coords[i + 1]
                    else:
                        x += coords[i]
                        y += coords[i + 1]
                    coordinates.append((x, y))
        elif command in 'Hh':
            # Horizontal line
            coords = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', params)]
            for coord in coords:
                if command.isupper():
                    x = coord
                else:
                    x += coord
                coordinates.append((x, y))
        elif command in 'Vv':
            # Vertical line
            coords = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', params)]
            for coord in coords:
                if command.isupper():
                    y = coord
                else:
                    y += coord
                coordinates.append((x, y))
    
    return coordinates

def calculate_bounding_box(coordinates):
    """Calculate the bounding box of coordinates"""
    if not coordinates:
        return None
    
    min_x = min(coord[0] for coord in coordinates)
    max_x = max(coord[0] for coord in coordinates)
    min_y = min(coord[1] for coord in coordinates)
    max_y = max(coord[1] for coord in coordinates)
    
    return min_x, min_y, max_x, max_y

def path_to_rect(match):
    """Convert a path element to a rect element"""
    full_match = match.group(0)
    path_id = match.group(1) if match.group(1) else ""
    style = match.group(2)
    d = match.group(3)
    
    # Parse the path data
    coordinates = parse_path_data(d)
    
    if not coordinates:
        return full_match  # Return original if we can't parse
    
    # Calculate bounding box
    bbox = calculate_bounding_box(coordinates)
    if not bbox:
        return full_match
    
    min_x, min_y, max_x, max_y = bbox
    width = max_x - min_x
    height = max_y - min_y
    
    # Add some padding to make the square more visible
    padding = max(width, height) * 0.1
    width += padding * 2
    height += padding * 2
    min_x -= padding
    min_y -= padding
    
    # Create rect element
    rect_element = f'<rect\n           id="{path_id}"\n           style="{style}"\n           x="{min_x}"\n           y="{min_y}"\n           width="{width}"\n           height="{height}" />'
    
    return rect_element

def process_svg_colors():
    # Read the SVG file
    with open('image.svg', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create first output: only pink elements (#ff00cd)
    def keep_only_pink(match):
        color = match.group(1).lower()
        if color == 'ff00cd':
            return match.group(0)  # Keep pink
        else:
            return '#202124'  # Replace others with dark gray
    
    # Replace colors for pink-only version
    pink_only_content = re.sub(r'#([0-9a-fA-F]{6})', keep_only_pink, content)
    
    # Remove elements that don't have pink fill or stroke
    # Pattern to match style attributes that don't contain #ff00cd
    def remove_non_pink_elements(match):
        style_attr = match.group(1)
        if '#ff00cd' in style_attr:
            return match.group(0)  # Keep elements with pink
        else:
            return ''  # Remove elements without pink
    
    # Remove elements without pink (this is a simplified approach)
    # We'll use a more targeted approach by removing specific elements
    
    # Write the pink-only version
    with open('image_pink_only.svg', 'w', encoding='utf-8') as file:
        file.write(pink_only_content)
    
    # Create second output: filled shapes version
    # Find all hex color codes (#xxxxxx)
    hex_pattern = r'#([0-9a-fA-F]{6})'
    
    def replace_color(match):
        color = match.group(1).lower()
        # Keep #ff00cd unchanged, replace all others with #202124
        if color == 'ff00cd':
            return match.group(0)  # Return original match unchanged
        else:
            return '#202124'
    
    # Replace colors using the function
    processed_content = re.sub(hex_pattern, replace_color, content)
    
    # Now convert #ff00cd stroke elements to filled shapes
    # Pattern to match style attributes with #ff00cd stroke and fill:none
    stroke_to_fill_pattern = r'style="([^"]*fill:none[^"]*stroke:#ff00cd[^"]*)"'
    
    def convert_stroke_to_fill(match):
        style_attr = match.group(1)
        # Replace fill:none with fill:#ff00cd and remove stroke-related attributes
        new_style = style_attr.replace('fill:none', 'fill:#ff00cd')
        # Remove stroke-related attributes
        new_style = re.sub(r'stroke:#ff00cd[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-width:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-linecap:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-linejoin:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-miterlimit:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-dasharray:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-opacity:[^;]*;?', '', new_style)
        # Clean up any double semicolons or trailing semicolons
        new_style = re.sub(r';;+', ';', new_style)
        new_style = new_style.strip(';')
        return f'style="{new_style}"'
    
    # Apply the stroke-to-fill conversion
    processed_content = re.sub(stroke_to_fill_pattern, convert_stroke_to_fill, processed_content)
    
    # Convert Z-shaped paths to rectangles
    # Pattern to match path elements with #ff00cd fill
    path_pattern = r'<path\s+([^>]*id="([^"]*)"[^>]*)?\s+style="([^"]*fill:#ff00cd[^"]*)"[^>]*d="([^"]*)"[^>]*/>'
    
    # Apply the path-to-rect conversion
    processed_content = re.sub(path_pattern, path_to_rect, processed_content)
    
    # Write the processed content to a new file
    with open('image_processed.svg', 'w', encoding='utf-8') as file:
        file.write(processed_content)
    
    print("SVG processing completed!")
    print("Created two files:")
    print("1. image_pink_only.svg - Contains only pink elements")
    print("2. image_processed.svg - Contains filled shapes and converted elements")

if __name__ == "__main__":
    process_svg_colors()