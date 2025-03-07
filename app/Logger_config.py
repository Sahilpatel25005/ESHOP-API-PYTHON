import logging


# file_handler = logging.FileHandler('app.log', mode='a')
stream_handler = logging.StreamHandler()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[stream_handler]  # Append to the log file ],
)

logger = logging.getLogger('my_project_logger')