import subprocess
import os
import csv
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple

try:
    from colorama import init, Fore
    init(autoreset=True)  # Ensure color support on Windows
except ImportError:
    class Fore:
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        RESET = '\033[0m'

@dataclass
class MessageType:
    text: str
    type: str  # 'Error', 'Warning', or 'Info'

def categorize_message(text: str) -> str:
    """Categorize message based on content"""
    text_lower = text.lower()
    if any(word in text_lower for word in ['error', 'exception', 'failed', 'failure']):
        return 'Error'
    elif any(word in text_lower for word in ['warning', 'warn', 'caution']):
        return 'Warning'
    else:
        return 'Info'

def execute_command(command: str) -> Tuple[bool, str, str]:
    """Execute a shell command and return its output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def process_output(text: str) -> List[MessageType]:
    """Process text and categorize each line"""
    messages = []
    for line in text.split('\n'):
        if line.strip():
            message_type = categorize_message(line)
            messages.append(MessageType(line.strip(), message_type))
    return messages

def get_colored_text(text: str, message_type: str) -> str:
    """Return color-coded text for CSV output"""
    color_map = {
        'Error': Fore.RED,
        'Warning': Fore.YELLOW,
        'Info': Fore.BLUE
    }
    return f"{color_map.get(message_type, Fore.BLUE)}{text}{Fore.RESET}"

def save_to_csv(command: str, messages: List[MessageType], filename: str):
    """Save processed output to CSV file with colored text"""
    
    # Check if file exists
    file_exists = os.path.isfile(filename)

    # Prepare CSV headers and rows
    headers = ["Message Type", "Message"]
    rows = []

    # Add messages with colored text
    for msg in messages:
        rows.append([msg.type, get_colored_text(msg.text, msg.type)])
        if msg.type == "Error":
            rows.append(["", ""])  # Add a blank line after errors

    # Append to CSV instead of overwriting
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:  # Write headers only if file does not exist
            writer.writerow(["Command Executed:", command])
            writer.writerow(headers)
        writer.writerows(rows)

    return filename

def print_colored(text: str, message_type: str):
    """Print text with appropriate color based on message type"""
    color_map = {
        'Error': Fore.RED,
        'Warning': Fore.YELLOW,
        'Info': Fore.BLUE
    }
    print(f"{color_map.get(message_type, Fore.BLUE)}{text}{Fore.RESET}")

if __name__ == "__main__":
    # Your command
    command = "python pyQuARC/main.py --concept_ids C1000000010-CDDIS --format umm-c"

    # Output filename (fixed name to keep appending)
    csv_file = f'command_output.csv'

    print_colored(f"Executing command: {command}", "Info")
    print("-" * 50)

    # Execute command
    success, stdout, stderr = execute_command(command)

    # Process output
    messages = process_output(stdout) if success else [MessageType(stderr.strip(), 'Error')]

    # Display output in terminal with colors
    for msg in messages:
        print_colored(msg.text, msg.type)

    # Save to CSV
    saved_file = save_to_csv(command, messages, csv_file)
    print("-" * 50)
    print_colored(f"Output has been saved to: {saved_file}", "Info")
