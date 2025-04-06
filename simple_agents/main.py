import gradio as gr
import logging
import os
from simple_agents.coordinator_assistant import CoordinatorAssistant

# Get the absolute path for the log file
LOG_FILE = os.path.abspath('chat.log')
print(f"Log file will be created at: {LOG_FILE}")

class HTTPFilter(logging.Filter):
    """Filter out HTTP request logs."""
    def filter(self, record):
        # Only filter out actual HTTP request/response logs
        return not (
            record.getMessage().startswith("HTTP Request:") or 
            record.getMessage().startswith("response:") or
            record.getMessage().startswith("GET") or
            record.getMessage().startswith("POST")
        )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Get the root logger
logger = logging.getLogger()

# Add HTTP filter to all handlers
for handler in logger.handlers:
    handler.addFilter(HTTPFilter())

# Test logging
logger.info("Test log message")
print(f"Log file exists: {os.path.exists(LOG_FILE)}")
if os.path.exists(LOG_FILE):
    print(f"Log file size: {os.path.getsize(LOG_FILE)} bytes")

assistant = CoordinatorAssistant()

def clear_chat_log():
    """Clear the chat log file if it exists and exceeds 1MB in size."""
    if os.path.exists('chat.log'):
        file_size = os.path.getsize('chat.log')
        # 1MB = 1024 * 1024 bytes
        if file_size > 1024 * 1024:
            os.remove('chat.log')
            # Reconfigure logging to create a new log file
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('chat.log'),
                    logging.StreamHandler()
                ]
            )
            return f"Chat log cleared! (Previous size: {file_size / (1024*1024):.2f}MB)"
        return f"Chat log not cleared. Current size: {file_size / (1024*1024):.2f}MB"
    return "No chat log file found."

def chat_with_assistant(user_input, history):
    try:
        # Log the user's query
        logger.info(f"User Query: {user_input}")
        
        # Join conversation history to pass into the formatter LLM
        full_history = "\n".join([f"User: {u}\nAssistant: {a}" for u, a in history])
        full_prompt = f"{full_history}\nUser: {user_input}"

        # Log the coordinator's initial message to other agents
        logger.info(f"Coordinator -> Agents: {full_prompt}")
        
        response = assistant.run(full_prompt)
        
        return response
    except Exception as e:
        error_msg = f"[Error] {e}"
        logger.error(f"Error occurred: {error_msg}")
        return error_msg

def get_latest_log_trace(user_input):
    """Get the latest log entries for a query."""
    log_entries = []
    try:
        with open('chat.log', 'r') as f:
            lines = f.readlines()
            # Get the last 10 lines that contain this query
            for line in reversed(lines):
                if user_input in line:
                    # Include this line and the next 10 lines
                    idx = lines.index(line)
                    log_entries = lines[idx:idx+10]
                    break
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        return "Error reading log file"
    
    return "".join(log_entries)

def respond(message, chat_history):
    """Process the message and update chat history."""
    response = chat_with_assistant(message, chat_history)
    chat_history.append((message, response))
    log_trace = get_latest_log_trace(message)
    return "", chat_history, log_trace

# Create the main interface
with gr.Blocks(title="🧠 Simple Agents") as demo:
    gr.Markdown("# 🧠 Simple Agents")
    
    # Add a button to clear the chat log
    with gr.Row():
        clear_btn = gr.Button("Clear Chat Log")
        clear_output = gr.Textbox(label="Status", interactive=False)
    
    # Create the chat interface
    chat_interface = gr.ChatInterface(
        fn=chat_with_assistant,
        examples=["What is the current price of Bitcoin in USD?", "What's the weather in Tokyo today?"],
        title="Chat with Assistant",
        theme="soft"
    )
    
    # Connect the clear button to the clear function
    clear_btn.click(
        fn=clear_chat_log,
        outputs=clear_output
    )

if __name__ == "__main__":
    demo.launch(share=True)



