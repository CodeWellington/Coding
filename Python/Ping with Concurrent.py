import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time


def read_input(input_file):
    # Reading the input file with hostames/IPs
    with open(input_file, "r") as file:
        user_input = file.read().split()
    return user_input

def retry_time_num():
    # Asking user for the retry time number
    while True:
        try:
            retry = int(input("Please specify a number os attempts for unreachable devices: "))
            break
        except ValueError:
            print("Invalid input!")
    return retry

def retry_unreachable(retry_count, message, dev):
    # Retry is unreachable as per users input value
    retry_log = []
    attempt = 1

    # First attempt
    trying = f"Attempt {attempt}: " + message
    retry_log.append(trying)

    while retry_count > 0:
        retry_count -= 1
        attempt += 1

        # Sending the command again
        message, status = ping_dev(dev)

        trying = f"Attempt {attempt}: " + message
        retry_log.append(trying)

        # If device is now reachable we can stop the loop
        if status["reachable"]:
            break

    return retry_log

def write_file(log_file, log):
    # Writing the logs
    with open(log_file, "a+") as file:
        for line in log:
            file.write(line + "\n")

def time_now():
    # Time to log with timestamp
    time = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    return time

def ping_dev(dev):
    status = {
        "dns_error": False,
        "not_rea_error": False,
        "reachable": False,
    }

    # Run the ping from subprocess
    command = subprocess.run(f"ping {dev}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Checking DNS
    if "Ping request could not find host" in command.stdout:
        message = f"DNS entry not found for {dev} at time: {time_now()}"
        status["dns_error"] = True

    # Checking if device is not reachable
    elif command.returncode != 0:
        message = f"{dev} is not reachable at time: {time_now()}"
        status["not_rea_error"] = True

    # Checking if device is reachable
    elif command.returncode == 0:
        message = f"{dev} is reachable at time: {time_now()}"
        status["reachable"] = True
    else:
        message = f"{dev} is undetermined at time: {time_now()}"

    return message, status


retry = retry_time_num()

def main():
    input_file = r"hostname.txt"
    log_file = "log_with_multi_thread.txt"
    retry_count = retry
    log = []

    # Each device from input file

    devices = read_input(input_file)

    with ThreadPoolExecutor(max_workers=20) as executor:  # Recommend from 5-20 workers
        future_to_device = {executor.submit(ping_dev, dev): dev for dev in devices}

        # Process each result as they complete
        for future in future_to_device:
            dev = future_to_device[future]
            message, status = future.result()

            # Retry if not reachable
            if not status["reachable"]:
                log.extend(retry_unreachable(retry_count, message, dev))
            else:
                log.append(message)


    write_file(log_file, log)

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Total time taken: {elapsed_time:.4f} seconds")




