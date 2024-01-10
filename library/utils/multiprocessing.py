from multiprocessing import Pool
import concurrent.futures

from library.utils.utils import Utils


class Multiprocessing:
    pool_size = 4
    pool = Pool(pool_size)

    @staticmethod
    def multiproc(func, args):
        Utils.monitor_cpu_ram()

        response = Multiprocessing.pool.map(func, args)

        return response

    @staticmethod
    def concurrent_func(func, args):
        response = [None] * len(args)

        Utils.monitor_cpu_ram()

        with concurrent.futures.ThreadPoolExecutor(max_workers=Multiprocessing.pool_size) as executor:
            future = [executor.submit(func, url) for url in args]
            for i, f in enumerate(concurrent.futures.as_completed(future)):
                response[i] = f.result()

        return response
