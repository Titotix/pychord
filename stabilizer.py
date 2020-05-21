from threading import Thread, Event
import time

class Stabilizer(object):
    def __init__(self, local_node):
        self.node = local_node
        self.stop_event = Event()
        self.th = Thread(
            target=Stabilizer.stabilizer_loop,
            args=(self, self.stop_event, self.node)
        )

    def stop(self):
        self.stop_event.set()

    def start(self):
        self.th.start()

    def stabilizer_loop(self, stop_event, node, secs=1):
        """
        @param secs: time, in second, to repeat the loop
        """
        while not stop_event.is_set():
            node._stabilize_and_fix_fingers()
            time.sleep(secs)
