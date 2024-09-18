import requests
import time
from colorama import Fore, Style

# Function to read all authorization tokens from query.txt
def get_authorization_tokens():
    with open('query.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Function to set headers with the provided token
def get_headers(token):
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "x-telegram-web-app-data": f"{token}",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"127\", \"Chromium\";v=\"127\", \"Microsoft Edge WebView2\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://catsdogs.live/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

def fetch_tasks(headers): 
    url = "https://api.catsdogs.live/tasks/list"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # The response is already a list
    else:
        response.raise_for_status()

def clear_task(task_id, headers):
    url = "https://api.catsdogs.live/tasks/claim"
    payload = {"task_id": task_id}  # Prepare the payload with the correct key
    response = requests.post(url, json=payload, headers=headers)  # Use POST for claiming a task
    
    if response.status_code == 200:
        print(Fore.GREEN + f"Task {task_id} successfully marked as completed.")
        return response.json()
    else:
        print(Fore.RED + f"Failed to mark task {task_id} as completed.")
        response.raise_for_status()

def countdown_timer(seconds):
    while seconds:
        print(Fore.YELLOW + f"Waiting {seconds} seconds before the next task...", end="\r")
        time.sleep(1)
        seconds -= 1
    print(Fore.YELLOW + "Proceeding to the next task..." + " " * 20)  # Clear the line

def complete_all_tasks(headers, confirm_clear_tasks):
    if not confirm_clear_tasks:
        return
    
    tasks = fetch_tasks(headers)  # Get the list of tasks
    
    for task in tasks:
        task_id = task.get('id')  # Use 'id' from the task data
        
        if task_id:
            try:
                clear_task(task_id, headers)  # Complete the task by its ID
                countdown_timer(10)  # Optional: Add a delay between tasks
            except requests.RequestException:
                print(Fore.WHITE + f"Skipping task {task_id} due to an error.")

def user(): 
    tokens = get_authorization_tokens()
    all_user_data = []
    
    for token in tokens:
        headers = get_headers(token)
        url = "https://api.catsdogs.live/user/info"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()  # Get the entire response
            
            # Extract required fields
            user_id = data.get('id', 'N/A')
            username = data.get('username', 'N/A')
            race = data.get('race', 'N/A')
            inviter_id = data.get('inviter_id', 'N/A')
            claimed_at = data.get('claimed_at', 'N/A')
            created_at = data.get('created_at', 'N/A')
            premium = data.get('premium', 'N/A')
            invite_reward = data.get('invite_reward', 'N/A')
            
            # Collect user data
            all_user_data.append([user_id, username, race, inviter_id, claimed_at, created_at, premium, invite_reward])
        else:
            print(Fore.RED + f"Failed to fetch user data for token {token}. Status code: {response.status_code}")
            response.raise_for_status()
    
    # Print user data
    print(Fore.WHITE + "User Data:")
    for user_info in all_user_data:
        print(user_info)

def main():
    print(Fore.GREEN + Style.BRIGHT + "Duck BOT")
    
    # Ask the user once if they want to complete all tasks
    confirmation = input(Fore.WHITE + f"Do you want to complete all tasks automatically? (y/n): ").strip().lower()
    confirm_clear_tasks = confirmation == 'y'
    
    while True:
        try:
            print(Fore.WHITE + f"\nDisplaying user information...")
            user()
            print(Fore.WHITE + f"\n............................")
            
            tokens = get_authorization_tokens()
            for token in tokens:
                headers = get_headers(token)
                
                # Display and fetch tasks for the current token
                print(Fore.WHITE + f"\nDisplaying Task information for token {token[:20]}...")
                tasks = fetch_tasks(headers)
                
                if tasks:
                    print(Fore.WHITE + "Task data received.")
                    # Auto complete tasks for the current token, without asking again
                    if confirm_clear_tasks:
                        print(Fore.WHITE + f"\nRun auto complete task for token {token[:20]}...")
                        complete_all_tasks(headers, confirm_clear_tasks)
                
                print(Fore.WHITE + f"\n............................")
                print(Fore.YELLOW + f"Waiting for the next token...\n")
        
        except KeyboardInterrupt:
            print(Fore.RED + "\nBot stopped by user.")
            break
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()
