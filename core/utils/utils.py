def queue_to_list(q):
    """
    Dumps the content of a queue into a python list.
    """
    created_list = []
    while not q.empty():
        created_list.append(q.get())

    return created_list


def parse_IPs(raw):
    """
    Function to parse an IP list seperated by commas
    """
    raw = "".join(raw.split())
    ips = raw.split(',')

    return ips


class Queue:
    """
    Simple FIFO queue class based on the python list
    """
    def __init__(self, max_length=0):
        self.queue = []
        self.max_length = max_length

    def full(self):
        """
        Returns true if the list is full
        """
        return self.max_length == len(self.queue)

    def put(self, item):
        """
        Puts an item at the end of the list and removes the first one
        if the queue is full
        """
        self.queue.append(item)

        if len(self.queue) > self.max_length and len(self.queue) > 0:
            self.queue.pop(0)

    def last(self):
        """
        Returns the last element from the queue
        """
        if len(self.queue) > 0:
            return self.queue[-1]

    def dump(self):
        """
        Returns the current queue
        """
        return self.queue
