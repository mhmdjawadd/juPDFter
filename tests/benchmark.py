import time
from file_processor import process_file

def benchmark_process_file():
    start_time = time.time()
    result = process_file('test.txt')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processing Time: {elapsed_time:.6f} seconds")
    print(result)
    # Optionally, assert something about the result
    # assert result is not None

if __name__ == "__main__":
    benchmark_process_file() 