#!/usr/bin/env python3
"""
Mock Claude-Code process for testing.

This simulates a Claude-Code session for testing the supervisor functionality.
"""

import sys
import time
import signal

def main():
    """Mock Claude-Code main function."""
    print("Claude-Code Mock Session Started")
    print("Type 'help' for available commands")

    try:
        while True:
            # Read input (this simulates Claude-Code waiting for commands)
            try:
                user_input = input("> ")

                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("  help - Show this help")
                    print("  status - Show session status")
                    print("  echo [text] - Echo back the text")
                    print("  wait - Simulate a long-running task")
                    print("  error - Simulate an error")
                    print("  exit/quit - Exit the session")
                elif user_input.lower() == 'status':
                    print("Session Status: Active")
                    print("Working Directory:", "/tmp/mock-session")
                    print("Uptime:", "5 minutes")
                elif user_input.lower().startswith('echo'):
                    echo_text = user_input[5:].strip()
                    print(f"Echo: {echo_text}")
                elif user_input.lower() == 'wait':
                    print("Starting long-running task...")
                    for i in range(5):
                        print(f"Progress: {i+1}/5")
                        time.sleep(1)
                    print("Task completed!")
                elif user_input.lower() == 'error':
                    print("ERROR: Simulated error occurred!")
                    print("This is what an error looks like in Claude-Code")
                else:
                    print(f"I don't understand '{user_input}'. Type 'help' for available commands.")

            except EOFError:
                # This happens when the input stream is closed
                print("\nInput stream closed. Exiting...")
                break
            except KeyboardInterrupt:
                print("\nReceived interrupt signal. Exiting...")
                break

    except Exception as e:
        print(f"Mock Claude-Code error: {e}")
        sys.exit(1)

def signal_handler(signum, frame):
    """Handle termination signals."""
    print(f"\nReceived signal {signum}. Shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()