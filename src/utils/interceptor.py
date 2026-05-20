# src/utils/interceptor.py
import functools
import logging
import os

# Set up a dedicated logs folder at the root of the project
# Using os.path ensures this works smoothly on Windows
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure the logger to write to a file
LOG_FILE = os.path.join(LOG_DIR, "tool_calls.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

def log_tool_call(func):
    """
    A decorator that intercepts a tool execution to log its metadata.
    Matches the strict requirement: Tool Name, Input Parameters, and Output.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Capture Tool Name
        tool_name = func.__name__
        
        # 2. Capture Input Parameters (merging positional and keyword args)
        inputs = kwargs if kwargs else args
        if not inputs:
            inputs = "None"
            
        try:
            # Execute the actual tool function
            output = func(*args, **kwargs)
            
            # 3. Capture Output and build the final log string
            log_message = f"Tool Name: {tool_name} | Input Parameters: {inputs} | Output: {output}"
            
            # Write to the .log file
            logging.info(log_message)
            
            # Optional: Print to your terminal so you can see it working in real-time
            print(f"\n[INTERCEPTOR] {log_message}")
            
            return output
            
        except Exception as e:
            # If the tool crashes, log the error so the agent doesn't fail silently
            error_message = f"Tool Name: {tool_name} | Input Parameters: {inputs} | ERROR: {str(e)}"
            logging.error(error_message)
            print(f"\n[INTERCEPTOR ERROR] {error_message}")
            raise e
            
    return wrapper