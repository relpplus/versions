import time

def get_elapsed_time(start_time):
    end_time = time.time()
    return f'{end_time - start_time:.4f}s' 