import os
import sys

# --- DEPENDENCY CHECK ---
# We use svglib/reportlab because standard FFmpeg builds on Windows 
# often lack the specific 'librsvg' decoder needed for SVGs.
try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
except ImportError:
    print("--- MISSING PYTHON LIBRARIES ---")
    print("This script requires 'svglib' and 'reportlab' to convert SVGs.")
    print("Please run this command in your terminal/command prompt:")
    print("\n    pip install svglib reportlab")
    print("\n(Then run this script again)")
    input("\nPress Enter to exit...")
    sys.exit(1)

def convert_svgs_recursively():
    # scan_directory = current folder where this script is placed
    scan_directory = os.getcwd()

    print(f"--- Starting SVG to PNG Batch Converter (Native Python) ---")
    print(f"Target Directory: {scan_directory}")
    print("Scanning for SVGs...")

    converted_count = 0
    error_count = 0
    skipped_count = 0

    # --- MAIN LOOP ---
    for root, dirs, files in os.walk(scan_directory):
        for filename in files:
            if filename.lower().endswith(".svg"):
                full_svg_path = os.path.join(root, filename)
                
                # Create the new PNG path in the same folder
                file_name_no_ext = os.path.splitext(filename)[0]
                full_png_path = os.path.join(root, f"{file_name_no_ext}.png")

                # Optional: Skip if PNG already exists to save time? 
                # Currently set to overwrite (consistent with previous request)
                
                print(f"Converting: {filename}...")

                try:
                    # 1. Read the SVG file
                    drawing = svg2rlg(full_svg_path)
                    
                    if drawing:
                        # 2. Render to PNG
                        # If the icons are too small (e.g. 24x24), you can scale them up
                        # by uncommenting the next line:
                        # drawing.scale(2, 2)  # Scales image 2x bigger
                        
                        renderPM.drawToFile(drawing, full_png_path, fmt="PNG")
                        
                        print(f"   -> Done: {file_name_no_ext}.png")
                        converted_count += 1
                    else:
                        print(f"   -> FAILED: File appears empty or corrupted.")
                        error_count += 1

                except Exception as e:
                    print(f"   -> ERROR: {e}")
                    error_count += 1
    
    # --- SUMMARY ---
    print(f"\n--- Operation Complete ---")
    print(f"Converted: {converted_count}")
    print(f"Errors:    {error_count}")
    
    input("\nPress Enter to close this window...")

if __name__ == "__main__":
    convert_svgs_recursively()