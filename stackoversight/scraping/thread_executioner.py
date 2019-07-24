import ctypes
import logging
import threading
from queue import Queue


class ThreadExecutioner:
    @staticmethod
    def mass_murder(victims: Queue):
        try:
            while True:
                victim = victims.get(block=True)
                ThreadExecutioner.murder(victim)

        except SystemExit:
            logging.info(f'System exit exception raised, {threading.current_thread().getName()} successfully killed.')

    @staticmethod
    def murder(victim: threading.Thread):
        alive = victim.is_alive()
        if alive:
            if not ctypes.pythonapi.PyThreadState_SetAsyncExc(victim, ctypes.py_object(SystemExit)):
                raise ChildProcessError
        else:
            logging.info(f'{victim.getName()} is dead, no need to kill prematurely.')

        victim.join()
        return alive

    @staticmethod
    def execute(target, tasks: Queue, *args):
        current_thread_name = threading.current_thread().getName()

        hit_queue = Queue()
        thread_killer = threading.Thread(target=ThreadExecutioner.mass_murder, args=[hit_queue], daemon=True)
        thread_killer.setName(f'{current_thread_name}\'s Thread Killer')
        thread_killer.start()

        logging.info(f'New killer, {thread_killer.getName()}, spawned.')

        try:
            worker_count = 0

            while True:
                task = tasks.get(block=True)

                worker = threading.Thread(target=target, args=(task, hit_queue, *args), daemon=True)
                worker.setName(f'{current_thread_name}\'s Worker #{worker_count}')
                worker.start()

                logging.info(f'New worker, {worker.getName()}, spawned for task {task}.')

                worker_count += 1
        except SystemExit:
            logging.info(f'System exit exception raised, {current_thread_name}\'s killer will now be killed.')

            ThreadExecutioner.murder(thread_killer)

            logging.info(f'{current_thread_name} successfully killed')
