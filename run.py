import sys
import os

# Add the current directory to sys.path to ensure src can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    main()
