import logging
import sys

formatter = logging.Formatter(
    '%(asctime)s [PID:%(process)d] [%(name)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# logging.basicConfig(
#     level=logging.INFO,  # Set default level to INFO
#     format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

# Create console handler for all logs
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

# =====================================
# STEP 1: Configure the ROOT logger first
# =====================================
root_logger = logging.getLogger()

# Remove all existing handlers from root logger
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Set root logger level and add our handler
root_logger.setLevel(logging.WARNING)  # Default level for all loggers
root_logger.addHandler(console_handler)

# =====================================
# STEP 2: Configure SQLAlchemy loggers
# =====================================
for logger_name in [
    'sqlalchemy',
    'sqlalchemy.engine',
    'sqlalchemy.pool',
    'sqlalchemy.dialects',
    'sqlalchemy.orm'
]:
    sql_logger = logging.getLogger(logger_name)
    
    # Remove all existing handlers
    for handler in sql_logger.handlers[:]:
        sql_logger.removeHandler(handler)
    
    # Set to WARNING to suppress SQL queries
    sql_logger.setLevel(logging.WARNING)
    
    # Prevent propagation to avoid double logging
    sql_logger.propagate = False
    
    # Add our console handler directly
    sql_logger.addHandler(console_handler)

# =====================================
# STEP 3: Configure our application logger
# =====================================
logger = logging.getLogger("app")

# Remove any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Set app logger to DEBUG for verbose app logs
logger.setLevel(logging.DEBUG)

# Prevent propagation to avoid double logging
logger.propagate = False

# Add our console handler
logger.addHandler(console_handler)