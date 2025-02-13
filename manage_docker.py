import subprocess
import os
import time
import sys

# ANSI escape sequences for colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def clear_screen():
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

def is_container_running(container_name):
    # Check if a Docker container with the specified name is running
    result = subprocess.run(["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"], capture_output=True, text=True)
    return container_name in result.stdout

def start_application():
    # Start the application if the containers are not already running
    if is_container_running("lasko_app") and is_container_running("lasko_cassandra"):
        print(f"{YELLOW}Lasko Backend and Cassandra are already running.{RESET}")
        input(f"{YELLOW}Press Enter to return to the menu...{RESET}")
    else:
        print(f"{GREEN}Starting Lasko Backend...{RESET}")
        subprocess.run(["docker", "compose", "up", "--build", "-d"])
        
        # Display a blinking message for 60 seconds to indicate Cassandra startup period
        for _ in range(30):  # 30 iterations for 60 seconds (2 seconds per iteration)
            sys.stdout.write(f"\r{YELLOW}Cassandra might take a few seconds to be fully active and ready to serve the Lasko Backend. Please wait patiently.{RESET}")
            sys.stdout.flush()
            time.sleep(1)
            sys.stdout.write("\r" + " " * 100)  # Clear the line
            sys.stdout.flush()
            time.sleep(1)

def stop_application():
    # Stop the running Docker containers
    print("Stopping Lasko application...")
    subprocess.run(["docker", "compose", "down"])

def show_status():
    # Show the status of all Docker containers related to Lasko
    result = subprocess.run(["docker", "ps", "-a", "--filter", "name=lasko_", "--format", "{{.Names}}"], capture_output=True, text=True)
    if result.stdout.strip():
        print(f"{BLUE}Showing status of all containers, including Cassandra...{RESET}")
        subprocess.run(["docker", "ps", "-a"])
    else:
        print(f"{YELLOW}No Lasko or Cassandra containers are currently running.{RESET}")

def remove_containers_and_images():
    # Remove all Docker containers and images for Lasko and Cassandra
    if is_container_running("lasko_app") or is_container_running("lasko_cassandra"):
        print(f"{RED}Removing all containers and images for Lasko and Cassandra...{RESET}")
        subprocess.run(["docker", "rm", "-f", "lasko_app", "lasko_cassandra"])
        subprocess.run(["docker", "rmi", "lasko_app_image", "cassandra"])
        subprocess.run(["docker", "volume", "rm", "lascaux-backend_cassandra_data"])
        print(f"{RED}Exiting and removing all containers and images for Lasko and Cassandra.{RESET}")
    else:
        print(f"{YELLOW}No Lasko or Cassandra containers are currently running to remove.{RESET}")

def stop_and_exit_without_removal():
    # Stop the containers without removing them
    if is_container_running("lasko_app") or is_container_running("lasko_cassandra"):
        print(f"{YELLOW}Stopping Lasko Backend and Cassandra containers without removing them...{RESET}")
        subprocess.run(["docker", "compose", "stop"])
    else:
        print(f"{YELLOW}No Lasko Backend or Cassandra containers are currently running to stop.{RESET}")

def main():
    # Main loop to display the menu and handle user input
    while True:
        clear_screen()
        print(f"\n{BLUE}Lasko Docker Backend Manager{RESET}")
        print(f"{GREEN}1. Start Lasko Backend{RESET}")
        print(f"{BLUE}2. Show Container Status (including Cassandra){RESET}")
        print(f"{YELLOW}3. Exit and Leave Running{RESET}")
        print(f"{RED}4. Stop and Exit Without Removing Containers and Images{RESET}")
        print(f"{RED}5. Stop, Exit and Remove All Containers and Images{RESET}")
        choice = input("Select an option: ")

        if choice == '1':
            start_application()
        elif choice == '2':
            show_status()
            input(f"{YELLOW}Press Enter to return to the menu...{RESET}")
        elif choice == '3':
            if is_container_running("lasko_app") or is_container_running("lasko_cassandra"):
                print(f"{YELLOW}Exiting and leaving Lasko Backend and Cassandra containers running.{RESET}")
            else:
                print(f"{YELLOW}Exiting. No Lasko Backend or Cassandra containers are currently running.{RESET}")
            break
        elif choice == '4':
            stop_and_exit_without_removal()
            break
        elif choice == '5':
            remove_containers_and_images()
            break
        else:
            print(f"{RED}Invalid choice. Please try again.{RESET}")

if __name__ == "__main__":
    main() 
