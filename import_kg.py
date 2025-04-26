#!/usr/bin/env python
"""
Wrapper script for running my_extensions/import_kg.py from the root folder.
This allows backward compatibility after moving the script to my_extensions folder.
"""

import sys
import os

try:
    # Add the my_extensions directory to the Python path if needed
    extensions_dir = os.path.join(os.path.dirname(__file__), "my_extensions")
    if extensions_dir not in sys.path:
        sys.path.append(extensions_dir)
        
    # Import the main function from the relocated script
    from my_extensions.import_kg import main
    
    # Run the main function
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error importing from my_extensions/import_kg.py: {e}")
    print("Make sure the file exists and the my_extensions directory is in your Python path.")
    sys.exit(1)
except Exception as e:
    print(f"Error running import_kg.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 