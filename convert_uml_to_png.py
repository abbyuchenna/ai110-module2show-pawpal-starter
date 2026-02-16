"""
Convert Mermaid UML diagram to PNG using kroki.io API.
"""

import requests
import base64
import zlib

def mermaid_to_png(mermaid_code: str, output_path: str):
    """
    Convert Mermaid diagram to PNG using kroki.io API.

    Args:
        mermaid_code: The Mermaid diagram code
        output_path: Path where PNG should be saved
    """
    # Compress and encode the diagram
    compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')

    # Request PNG from kroki.io
    url = f"https://kroki.io/mermaid/png/{encoded}"

    print(f"Generating PNG from Mermaid diagram...")
    response = requests.get(url)

    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Successfully created: {output_path}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Read the Mermaid diagram
    with open("uml_diagram.mmd", "r") as f:
        mermaid_code = f.read()

    # Convert to PNG
    mermaid_to_png(mermaid_code, "uml_final.png")
