# For threading
import threading
# For victim queue
from queue import Queue
# For raising error
import ctypes


class ThreadExecutioner:
    @staticmethod
    def mass_murder(victims: Queue):
        try:
            while True:
                victim = victims.get(block=True)
                ThreadExecutioner.murder(victim)
        except SystemExit:
            print()
            # TODO: logging

    @staticmethod
    def murder(victim: threading.Thread):
        alive = victim.is_alive()
        if alive:
            if not ctypes.pythonapi.PyThreadState_SetAsyncExc(victim, ctypes.py_object(SystemExit)):
                raise ChildProcessError
        victim.join()

        return alive

    @staticmethod
    def execute(target, tasks: Queue, *args):
        hit_queue = Queue()
        thread_killer = threading.Thread(target=ThreadExecutioner.mass_murder, args=[hit_queue], daemon=True)
        thread_killer.start()

        try:
            while True:
                task = tasks.get(block=True)
                print(task)

                threading.Thread(target=target, args=(task, hit_queue, *args), daemon=True)

        except SystemExit:
            ThreadExecutioner.murder(thread_killer)
            print('Done scraping parent links')
