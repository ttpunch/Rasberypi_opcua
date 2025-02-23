import logging
import sys
from datetime import datetime

def get_logger(name):
    """Create and return a logger instance with a specific format."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Set logging level
        logger.setLevel(logging.INFO)
        
        # Create handlers
        file_handler = logging.FileHandler(f"../logs/backend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Add formatter to handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger