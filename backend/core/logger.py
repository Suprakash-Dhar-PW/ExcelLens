import logging
import sys
import os

def setup_logger():
    level = logging.DEBUG if os.getenv("DEBUG_LOG") == "1" else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("RevenueCommandCenter")

logger = setup_logger()
