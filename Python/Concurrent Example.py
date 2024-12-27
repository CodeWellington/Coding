from concurrent.futures import ThreadPoolExecutor
import time


def hostname(dev):
    time.sleep(10)
    return f" - Hostname is: {dev}"

def main():

    devices = [
        "RTR1",
        "RTR2",
        "SW1",
        "SW2"
    ]

    with ThreadPoolExecutor(max_workers=20) as executor:  # Recommend from 5-20 workers
        all_devices = {executor.submit(hostname, dev): dev for dev in devices}

          # Process each result as they complete
        for key, value in all_devices.items():
            result = key.result() # the key will be the value returned from the function
            dev = value # value is each line from the list "devices"
            print(dev)
            print(result)

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Total time taken: {elapsed_time:.4f} seconds")




