from multiprocessing import Pool
import threading
import _thread
import concurrent.futures
import requests

# will have functions to do stuff with the above packages

# create a new pool of processes
# num_processes = 4
pool = Pool(4)
def multiproc(func, num):
    response = []

    urls = pool.map(requests.get, ["https://en.wikipedia.org/wiki/Special:Random" for i in range(int(num))])
    response = pool.map(func, [url.url for url in urls])

    return response

def concurrent_func(func, num):
    response = [None] * int(num)
    urls = []
    for i in range(int(num)):
        urls.append(requests.get("https://en.wikipedia.org/wiki/Special:Random"))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = [executor.submit(func, url.url) for url in urls]
        for i, f in enumerate(concurrent.futures.as_completed(future)):
            response[i] = f.result()

    return response
