import json
import os
from PIL import Image

# Load the JSON data from the pokedex.json file
with open('pokedex.json', 'r') as f:
    pokedex = json.load(f)

# Create a dictionary to map Pokemon IDs to their English names
pokemon_names = {str(pokemon['id']).zfill(3): pokemon['name']['english'] for pokemon in pokedex}

def crop_image(img):
    # Convert image to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Get bounding box of non-white pixels
    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox)
    return img

def resize_image_if_needed(img, max_width=60, max_height=60):
    width, height = img.size

    # Check if either dimension exceeds the maximum allowed
    if width > max_width or height > max_height:
        # Calculate the scaling factor for both dimensions
        width_ratio = max_width / width
        height_ratio = max_height / height
        scale_factor = min(width_ratio, height_ratio)

        # Calculate new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
    return img


def images_to_html_tables(folder_path, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Initialize the index HTML content
    index_html_content = "<html><head><meta charset='UTF-8'></head><body style='font-family: sans-serif'><h1>Pokémon Beads Patterns / Pokémon Perlemønster</h1><p>Can be used with HAMA perler beads or iron beads of all brands / Kan brukes med alle rørperler fra Hama eller andre merker</p><ul>"
    
    # Get the list of files in alphabetical order
    files = sorted(os.listdir(folder_path))
    
    # Iterate through all files in alphabetical order
    for filename in files:
        if filename.endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            img = Image.open(image_path)
            
            # Convert paletted images to RGB
            if img.mode == 'P':
                img = img.convert('RGBA')
            else:    
                print("Image not converted from P mode.")
                print(filename)
            
            # Crop the image to remove blank or white pixels
            img = crop_image(img)
            
            
            
            # Reduce the number of colors to a maximum of 12
            img = img.quantize(colors=12, method=2).convert('RGBA')

            # Resize the image if needed
            img = resize_image_if_needed(img)

            width, height = img.size
            pixels = img.load()
            
            # If Image is more than 30 beads, write printing instructions "(stor)" - large in Norwegian
            if width > 52: 
                link_description = "  - XXL"
                title_description = " (Will not fit A4 horizontal)"
            elif width > 36:
                link_description = " - Large"
                title_description = " (Print A4 horizontal)"
            elif width > 31 or height > 31:
                link_description = " - Medium"
                title_description = " - Medium"
            else:
                link_description = ""
                title_description = ""

            # Style css for printing
            style_css = '<head> <style>.perle-number{font-size: 8px; text-align: center;}tr td {padding: 0;} tr td div{ height: 4.5mm; width: 4.5mm; border-right: 1px solid #000000; border-bottom: 1px solid #000000;} page[size="A4"] { width: 21cm; height: 29.7cm; display: block; margin: 0 auto; margin-bottom: 0.5cm; box-shadow: 0 0 0.5cm rgba(0,0,0,0.5); } @media print { body, page[size="A4"] { margin: 0; box-shadow: 0; -webkit-print-color-adjust:exact !important; print-color-adjust:exact !important; } } </style> </head>'

            # Extract the file ID from the filename
            file_id = os.path.splitext(filename)[0]
            # Check if the file ID is in the correct format and exists in the Pokemon names dictionary
            if file_id in pokemon_names:
                # Get the Pokemon name
                pokemon_name = pokemon_names[file_id]
                html_filename = f"{file_id}.html"
                index_html_content += f"<li><a href='{html_filename}'>{pokemon_name}{link_description}</a></li>"
                html_content = f"<html>{style_css}<body style='font-family: sans-serif'><h2>{pokemon_name}{title_description}</h2>"
            else:
                html_filename = f"{filename}.html"
                index_html_content += f"<li><a href='{html_filename}'>{file_id}{link_description}</a></li>"
                html_content = f"<html>{style_css}<body style='font-family: sans-serif'><h2>{filename}{title_description}</h2>"
            
            html_content += "<table style='border: none; border-collapse: collapse;'>"
            
            # Add the top row with numbers
            html_content += "<tr><td><div class='perle-number'>!</div></td>"  # Empty top-left cell
            for x in range(width):
                html_content += f"<td style=''><div class='perle-number'>{x}</div></td>"
            html_content += "</tr>"
            
            # Create table rows and cells
            used_colors = set()
            for y in range(height):
                html_content += f"<tr><td style=''><div class='perle-number'>{y}</div></td>"  # Left column with numbers
                for x in range(width):
                    pixel = pixels[x, y]
                    if img.mode == 'RGBA':
                        r, g, b, a = pixel
                    elif img.mode == 'RGB':
                        r, g, b = pixel
                        a = 255  # Default alpha value for RGB images
                    else:
                        raise ValueError(f"Unsupported image mode: {img.mode}")
                    #color = f"#{r:02x}{g:02x}{b:02x}"
                    color = f"rgba({r},{g},{b},{a})"
                    used_colors.add(color)
                    html_content += f"<td><div class='perle' style='background-color: {color};'></div></td>"
                html_content += "</tr>"
            
            # End the table
            html_content += "</table>"
            
            # Add the list of used colors
            html_content += "<table style=''><tr>"
            for color in sorted(used_colors):
                html_content += f"<td style='width: 32px; height: 32px; background-color: {color}; border: 1px solid black;'></td>"
            html_content += "</tr></table>"
            

            # Change to your attributon for output generated
            html_content += "<h6>Made with love in Oslo Norway, oslopokemon.com - </h6><h6>Licence <a href='https://creativecommons.org/licenses/by-nc/4.0/'>Attribution-NonCommercial 4.0</a></h6>"
            html_content += '<a href="https://www.freecounterstat.com" title="free hit counters"><img src="https://counter4.optistats.ovh/private/freecounterstat.php?c=86zpjj8lhp8cdp7r6gnrpl1mkjzfh4t9" border="0" title="free hit counters" alt="free hit counters"></a>'


            # End the html document
            html_content += "</body></html>"
            # Write the HTML content to the output file
            with open(os.path.join(output_folder, html_filename), "w") as file:
                file.write(html_content)
    
    # End the index HTML file
    index_html_content += "</ul><p>Made with <a href='https://github.com/kjartan-neon/image2perler'>image2perler</a></p></body></html>"
    
    # Write the index HTML content to the output file
    with open(os.path.join(output_folder, "index.html"), "w") as file:
        file.write(index_html_content)

# Example usage
images_to_html_tables("input-images/", "docs/")
