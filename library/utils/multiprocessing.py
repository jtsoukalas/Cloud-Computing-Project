from multiprocessing import Pool
import concurrent.futures

class Multiprocessing:
    pool_size = 4
    pool = Pool(pool_size)

    @staticmethod
    def multiproc(func, args):
        response = Multiprocessing.pool.starmap(func, args)

        return response

    @staticmethod
    def concurrent_func(func, args):
        response = [None] * len(args)

        with concurrent.futures.ThreadPoolExecutor(max_workers=Multiprocessing.pool_size) as executor:
            future = [executor.submit(func, url, True) for url in args]
            for i, f in enumerate(concurrent.futures.as_completed(future)):
                response[i] = f.result()

        return response
