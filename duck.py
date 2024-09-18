import requests
import time
from tabulate import tabulate
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
        "authorization": f"tma {token}",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"127\", \"Chromium\";v=\"127\", \"Microsoft Edge WebView2\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://tgdapp.duckchain.io/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

def fetch_tasks(headers):
    url = "https://preapi.duckchain.io/task/task_list"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        tasks_data = response.json().get('data', {})
        # Combine tasks from all categories into a single list
        all_tasks = []
        for task_category in ['social_media', 'daily', 'oneTime', 'partner']:
            all_tasks.extend(tasks_data.get(task_category, []))  # Add tasks from each category
        
        return all_tasks
    else:
        response.raise_for_status()



def clear_task(task_id, task_type, headers):
    url = f"https://preapi.duckchain.io/task/{task_type}?taskId={task_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print(Fore.GREEN + f"Task {task_id} ({task_type}) successfully marked as completed.")
        return response.json()
    else:
        print(Fore.RED + f"Failed to mark task {task_id} ({task_type}) as completed.")
        response.raise_for_status()


def print_welcome_message():
    print(Fore.GREEN + Style.BRIGHT + "Duck BOT")
    print(Fore.RED + Style.BRIGHT + "Join telegram https://t.me/dasarpemulung)\n\n")        

def check_task_completion(task_id, headers):
    url = "https://preapi.duckchain.io/task/task_info"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Check if task_id is present in the response data
        for task in data:
            if task.get('taskId') == task_id:
                print(Fore.YELLOW + f"Task {task_id} already completed.")
                return True
        # If task_id is not found
        return False
    else:
        print(Fore.RED + f"Failed to fetch task completion status.")
        print(Fore.RED + f"Status Code: {response.status_code}")
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
        task_id = task.get('taskId')
        task_type = task.get('taskType')  # Example: "follow_twitter", "join_tg_group", etc.
        
        if task_id and task_type:
            try:
                # Complete the task by its type and ID
                clear_task(task_id, task_type, headers)
                countdown_timer(10)  # Optional: Add a delay between tasks
            except requests.RequestException:
                print(Fore.WHITE + f"Skipping task {task_id} ({task_type}) due to an error.")


def user():
    tokens = get_authorization_tokens()
    all_user_data = []
    total_rewards_sum = 0
    
    for token in tokens:
        headers = get_headers(token)
        url = "https://preapi.duckchain.io/user/info"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json().get('data')  # Extract the 'data' key from the response
            if data:
                # Extract required fields
                duckname = data.get('duckName', 'N/A')
                quackTimes = data.get('quackTimes', 'N/A')
                point = int(data.get('decibels', '0'))
                
                # Sum up the total points (decibels)
                total_rewards_sum += point
                
                # Collect user data
                all_user_data.append([duckname, quackTimes, point])
            else:
                print(Fore.RED + "No user data found in the response.")
        else:
            print(Fore.RED + f"Failed to fetch user data for token {token}.")
            response.raise_for_status()
    
    # Prepare data for tabulate
    table_data = [
        ["Duck Name", "Quack Time", "Point"]
    ]
    table_data.extend(all_user_data)
    
    # Print table
    print(tabulate(table_data, headers='firstrow', tablefmt='grid'))
    
    # Print total rewards sum with color
    print(Fore.GREEN + f"\nTotal Rewards: " + Fore.WHITE + f"{total_rewards_sum}" + Style.RESET_ALL)



def play_game(headers):
    url = "https://preapi.duckchain.io/quack/execute?"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            # Extract relevant fields from the response
            result = data.get('result', False)
            decibel = data.get('decibel', '0')
            quack_records = data.get('quackRecords', [])
            quack_times = data.get('quackTimes', '0')
            
            # Display the result
            if result:
                print(Fore.GREEN + f"Game played successfully!")
                print(Fore.WHITE + f"Decibels earned: {decibel}")
                print(Fore.WHITE + f"Quack Records: {', '.join(quack_records)}")
                print(Fore.WHITE + f"Remaining Quack Times: {quack_times}")
                countdown_timer(10)
            else:
                print(Fore.RED + "Game play was not successful.")
            
            # If quackTimes > 0, allow the game to continue
            if int(quack_times) > 0:
                print(Fore.WHITE + f"QuackTimes available: {quack_times}, you can continue playing.")
            else:
                print(Fore.YELLOW + f"No QuackTimes remaining, please try again later.")
        else:
            print(Fore.RED + f"Failed to play the game. Status code: {response.status_code}")
            response.raise_for_status()
    
    except requests.RequestException as e:
        print(Fore.RED + f"Error occurred while trying to play the game: {e}")


def confirm_upgrade(headers):
    url = "https://birdx-api2.birds.dog/minigame/incubate/confirm-upgraded"
    
    # Making a POST request to the API
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'confirmed':
            print(Fore.GREEN + "Upgrade confirmed successfully.")
        else:
            print(Fore.YELLOW + f"Upgrade status: {data}")
    else:
        print(Fore.RED + f"Failed to confirm upgrade. Status Code: {response.status_code}")
        print(Fore.RED + f"Response Content: {response.text}")


def system_check(headers):
    system_url = "https://birdx-api.birds.dog/system"
    response = requests.get(system_url, headers=headers)
    
    if response.status_code == 200:
        system_data = response.json()
        countdown = system_data.get('countdown')
        has_news = system_data.get('hasNews')
        
        print(f"System Countdown: {countdown}")
        print(f"Has News Timestamp: {has_news}")
        return system_data
    else:
        print(f"Failed to check system. Status Code: {response.status_code}")
        return None

def upgrade(headers):
    # Fetch the incubation info
    upgrade_url = "https://birdx-api2.birds.dog/minigame/incubate/upgrade"
    upgrade_response = requests.get(upgrade_url, headers=headers)

    if upgrade_response.status_code == 200:
                print("Upgrade initiated successfully.")
    else:
                print(f"Failed to initiate upgrade. Status Code: {upgrade_response.status_code}")
                print(f"Response Content: {upgrade_response.text}")

def main():
    print_welcome_message()

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
                else:
                    print(Fore.RED + "No tasks available for this token.")
                
                # Auto complete tasks for the current token, without asking again
                if confirm_clear_tasks:
                    print(Fore.WHITE + f"\nRun auto complete task for token {token[:20]}...")
                    complete_all_tasks(headers, confirm_clear_tasks)
                
                # Play the game for the current token
                print(Fore.WHITE + f"\nRun game for token {token[:20]}...")
                play_game(headers)
                
                print(Fore.WHITE + f"\n............................")
                print(Fore.YELLOW + f"Waiting for the next token...\n")
        
        except KeyboardInterrupt:
            print(Fore.RED + "\nBot stopped by user.")
            sys.exit()
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}")


if __name__ == "__main__":
    main()