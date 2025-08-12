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
    
    # Find all hex color codes (#xxxxxx)
    hex_pattern = r'#([0-9a-fA-F]{6})'
    
    def replace_color(match):
        color = match.group(1).lower()
        # Keep #0000ff and #fb0505 unchanged, replace all others with #202124
        if color == '70ff00':
            return match.group(0)  # Return original match unchanged
        else:
            return '#202124'
    
    # Replace colors using the function
    processed_content = re.sub(hex_pattern, replace_color, content)
    
    # Now convert #70ff00 (green) and #fb0505 (pink) stroke elements to filled shapes
    # Pattern to match style attributes with #70ff00 or #fb0505 stroke and fill:none
    stroke_to_fill_pattern = r'style="([^"]*fill:none[^"]*stroke:#(70ff00|fb0505)[^"]*)"'
    
    def convert_stroke_to_fill(match):
        style_attr = match.group(1)
        stroke_color = match.group(2)  # Get the matched color (70ff00 or fb0505)
        
        # Replace fill:none with the appropriate fill color
        if stroke_color == '70ff00':
            new_style = style_attr.replace('fill:none', 'fill:#70ff00')
        else:  # fb0505
            new_style = style_attr.replace('fill:none', 'fill:#fb0505')
        
        # Remove stroke-related attributes
        new_style = re.sub(r'stroke:#(70ff00|fb0505)[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-width:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-linecap:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-linejoin:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-miterlimit:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-dasharray:[^;]*;?', '', new_style)
        new_style = re.sub(r'stroke-opacity:[^;]*;?', '', new_style)
        # Clean up any double semicolons or trailing semicolons
        new_style = re.sub(r';;+', ';', new_style)
        new_style = new_style.strip(';')
        # Add thick red border
        new_style += ';stroke:#ff0000;stroke-width:50'
        return f'style="{new_style}"'
    
    # Apply the stroke-to-fill conversion
    processed_content = re.sub(stroke_to_fill_pattern, convert_stroke_to_fill, processed_content)
    
    # Convert Z-shaped paths to rectangles
    # Pattern to match path elements with #70ff00 fill - updated for multi-line structure
    path_pattern = r'<path\s+[^>]*?style="([^"]*fill:#70ff00[^"]*)"[^>]*?d="([^"]*)"[^>]*?/>'
    
    def path_to_rect_updated(match):
        style = match.group(1)
        d = match.group(2)
        
        # Parse the path data
        coordinates = parse_path_data(d)
        
        if not coordinates:
            return match.group(0)  # Return original if we can't parse
        
        # Calculate bounding box
        bbox = calculate_bounding_box(coordinates)
        if not bbox:
            return match.group(0)
        
        min_x, min_y, max_x, max_y = bbox
        width = max_x - min_x
        height = max_y - min_y
        
        # Add some padding to make the square more visible
        padding = max(width, height) * 0.1
        width += padding * 2
        height += padding * 2
        min_x -= padding
        min_y -= padding
        
        # Add thick red border to the style
        if 'stroke:' not in style:
            style += ';stroke:#ff0000;stroke-width:50'
        else:
            # Replace existing stroke with red border
            style = re.sub(r'stroke:[^;]*', 'stroke:#ff0000', style)
            style = re.sub(r'stroke-width:[^;]*', 'stroke-width:50', style)
            if 'stroke-width:8' not in style:
                style += ';stroke-width:50'
        
        # Create rect element
        rect_element = f'<rect\n           style="{style}"\n           x="{min_x}"\n           y="{min_y}"\n           width="{width}"\n           height="{height}" />'
        
        return rect_element
    
    # Apply the path-to-rect conversion
    processed_content = re.sub(path_pattern, path_to_rect_updated, processed_content, flags=re.DOTALL)
    
    # Write the processed content to a new file
    with open('image_processed.svg', 'w', encoding='utf-8') as file:
        file.write(processed_content)
    
    print("SVG processing completed!")
    print("Original colors replaced with #202124 (except #70ff00)")
    print("#70ff00 stroke elements converted to filled shapes")
    print("Z-shaped paths converted to squares/rectangles")
    print("Output saved to: image_processed.svg")

if __name__ == "__main__":
    process_svg_colors()