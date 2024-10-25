import requests
import concurrent.futures
import time

# Your API endpoint
url = 'https://api.projectsbd.me/v1/ticket/trains'

# Number of requests
num_requests = 100000

# Number of threads (more threads = more concurrent pressure)
num_threads = 1000  # Set this to a higher value for more pressure

# Function to send a single request
def send_request():
    try:
        response = requests.get(url)
        # Print the status code of each request (optional)
        # print(f"Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# Main function to send requests concurrently
def send_requests_concurrently():
    start_time = time.time()
    
    # Use ThreadPoolExecutor with a larger number of threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_request) for _ in range(num_requests)]
        concurrent.futures.wait(futures)
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Completed {num_requests} requests in {total_time:.2f} seconds")

if __name__ == "__main__":
    send_requests_concurrently()
