import queue
import threading
from typing import Callable, Any

class XYZTask:
    """
    Represents a task that encapsulates a callable function and its arguments.

    Attributes:
        func (Callable[..., Any]): The function to be executed.
        args (Any): Positional arguments to be passed to the function.
        kwargs (Any): Keyword arguments to be passed to the function.
    """

    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any):
        """
        Initializes the task with a function and its arguments.

        Args:
            func (Callable[..., Any]): The function to execute.
            *args (Any): Positional arguments for the function.
            **kwargs (Any): Keyword arguments for the function.
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        """
        Executes the encapsulated function with the provided arguments.
        """
        self.func(*self.args, **self.kwargs)

def consume(q: queue.Queue[XYZTask]) -> None:
    """
    Continuously consumes and executes tasks from a queue.

    Args:
        q (queue.Queue[XYZTask]): The queue from which to consume tasks.

    Note:
        This function will run indefinitely until it encounters a `None` task,
        which signals the consumer to stop.
    """
    while True:
        task = q.get()
        if task is None:  # Stop signal
            break
        try:
            task.execute()
        except Exception as e:
            print(f"Task raised an exception: {e}")


class XYZThreading:
    """
    A threading pool manager that handles task execution across multiple threads.

    Attributes:
        n_thread (int): The number of threads in the pool.
        threads (list[threading.Thread]): The list of threads.
        queue (queue.Queue): The queue for storing tasks.
        started (bool): Indicates whether the thread pool has been started.
    """

    def __init__(self, n_thread: int):
        """
        Initializes the thread pool with the specified number of threads.

        Args:
            n_thread (int): The number of threads to use in the pool.
        """
        self.n_thread = n_thread
        self.threads = []
        self.queue = queue.Queue()
        self.started = False

    def add_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Adds a task to the queue.

        Args:
            func (Callable[..., Any]): The function to be executed.
            *args (Any): Positional arguments for the function.
            **kwargs (Any): Keyword arguments for the function.
        """
        self.queue.put(XYZTask(func, *args, **kwargs))

    def start(self) -> None:
        """
        Starts the thread pool, allowing threads to begin consuming tasks from the queue.

        Raises:
            RuntimeError: If the thread pool has already been started.
        """
        if self.started:
            raise RuntimeError("Thread pool has already been started.")
        self.started = True
        for i in range(self.n_thread):
            t = threading.Thread(target=consume, args=(self.queue,), name=f'consumer{i}')
            t.start()
            self.threads.append(t)

    def join(self) -> None:
        """
        Waits for all threads to finish their tasks.

        Note:
            This method sends a stop signal (`None`) to each thread before joining them.
        """
        # Add None to the queue to stop each thread
        for _ in range(self.n_thread):
            self.queue.put(None)
        for t in self.threads:
            t.join()

    def monitor(self, interval: float = 1.0) -> None:
        """
        Monitors the task queue size at regular intervals.

        Args:
            interval (float): The time in seconds between each queue size check.

        Note:
            This method will stop monitoring once the queue is empty.
        """
        while True:
            print(f"Queue size: {self.queue.qsize()}")
            if self.queue.empty():
                break
            time.sleep(interval)



if __name__ == '__main__':

    import time
    import random

    def print_task(message: str, delay: int = 1) -> None:
            time.sleep(delay)
            print(f"Task completed: {message}")
            if random.random() < 0.2:
                raise Exception("Task failed")
            return f"Task result: {message}"

    def test_xyz_threading():
        thread_pool = XYZThreading(n_thread=3)

        for i in range(12):
            thread_pool.add_task(print_task, f"Task {i+1}", delay=2)

        print("Starting thread pool...")
        thread_pool.start()
        thread_pool.monitor()
        thread_pool.join()
        print("All tasks completed.")

    test_xyz_threading()

    # ThreadPoolExecutor的使用方法
    print("=======================")

    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务到线程池
        futures = [
            executor.submit(print_task, f"Task {i+1}", delay=2) for i in range(5)
        ]

        # 处理完成的任务
        for future in as_completed(futures):
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Task failed: {e}")


