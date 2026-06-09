import logging
import sys

def setup_logger():
    logger = logging.getLogger("RevenueCommandCenter")
    # Set level based on DEBUG_LOG env variable (default INFO)
    import os
    level = logging.DEBUG if os.getenv("DEBUG_LOG") == "1" else logging.INFO
    logger.setLevel(level)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()
