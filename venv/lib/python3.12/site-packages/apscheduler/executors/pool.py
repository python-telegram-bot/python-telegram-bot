from abc import abstractmethod
import concurrent.futures

from apscheduler.executors.base import BaseExecutor, run_job


class BasePoolExecutor(BaseExecutor):
    @abstractmethod
    def __init__(self, pool):
        super(BasePoolExecutor, self).__init__()
        self._pool = pool

    def _do_submit_job(self, job, run_times):
        def callback(f):
            exc, tb = (f.exception_info() if hasattr(f, 'exception_info') else
                       (f.exception(), getattr(f.exception(), '__traceback__', None)))
            if exc:
                self._run_job_error(job.id, exc, tb)
            else:
                self._run_job_success(job.id, f.result())

        f = self._pool.submit(run_job, job, job._jobstore_alias, run_times, self._logger.name)
        f.add_done_callback(callback)

    def shutdown(self, wait=True):
        self._pool.shutdown(wait)


class ThreadPoolExecutor(BasePoolExecutor):
    """
    An executor that runs jobs in a concurrent.futures thread pool.

    Plugin alias: ``threadpool``

    :param max_workers: the maximum number of spawned threads.
    """

    def __init__(self, max_workers=10):
        pool = concurrent.futures.ThreadPoolExecutor(int(max_workers))
        super(ThreadPoolExecutor, self).__init__(pool)


class ProcessPoolExecutor(BasePoolExecutor):
    """
    An executor that runs jobs in a concurrent.futures process pool.

    Plugin alias: ``processpool``

    :param max_workers: the maximum number of spawned processes.
    """

    def __init__(self, max_workers=10):
        pool = concurrent.futures.ProcessPoolExecutor(int(max_workers))
        super(ProcessPoolExecutor, self).__init__(pool)
