def queue_to_list(q):
    """
    Dumps the content of a queue into a python list.
    """
    created_list = []
    while not q.empty():
        created_list.append(q.get())

    return created_list


def parse_IPs(raw):
    raw = "".join(raw.split())
    ips = raw.split(',')

    return ips


class Queue:
    def __init__(self, max_length=0):
        self.queue = []
        self.max_length = max_length

    def full(self):
        return self.max_length == len(self.queue)

    def put(self, item):
        self.queue.append(item)

        if len(self.queue) > self.max_length and len(self.queue) > 0:
            self.queue.pop(0)

    def last(self):
        if len(self.queue) > 0:
            return self.queue[-1]

    def dump(self):
        return self.queue
