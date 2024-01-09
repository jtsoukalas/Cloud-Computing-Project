from multiprocessing import Pool
import concurrent.futures
import requests

class Multiprocessing:
    pool_size = 4
    __pool = {}

    def __init__(self):
        self.__pool = Pool(self.pool_size)

    def multiproc(self, func, args):
        response = []

        # also insert args for func, all urls and True
        response = self.__pool.starmap(func, args)

        return response

    @staticmethod
    def concurrent_func(func, num):
        response = [None] * int(num)
        urls = []
        for i in range(int(num)):
            urls.append(requests.get("https://en.wikipedia.org/wiki/Special:Random"))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = [executor.submit(func, url.url, True) for url in urls]
            for i, f in enumerate(concurrent.futures.as_completed(future)):
                response[i] = f.result()

        return response
