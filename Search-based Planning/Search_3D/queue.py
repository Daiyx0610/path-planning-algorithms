import collections
import heapq


class QueueFIFO:
    """
    Class: QueueFIFO
    Description: QueueFIFO is designed for First-in-First-out rule.
    """

    def __init__(self):
        self.queue = collections.deque()

    def empty(self):
        return len(self.queue) == 0

    def put(self, node):
        self.queue.append(node)  # enter from back

    def get(self):
        return self.queue.popleft()  # leave from front


class QueueLIFO:
    """
    Class: QueueLIFO
    Description: QueueLIFO is designed for Last-in-First-out rule.
    """

    def __init__(self):
        self.queue = collections.deque()

    def empty(self):
        return len(self.queue) == 0

    def put(self, node):
        self.queue.append(node)  # enter from back

    def get(self):
        return self.queue.pop()  # leave from back


class QueuePrior:
    """
    Class: QueuePrior
    Description: QueuePrior reorders elements using value [priority]
    """

    def __init__(self):
        self.queue = []

    def empty(self):
        return len(self.queue) == 0

    def put(self, item, priority):
        heapq.heappush(self.queue, (priority, item))  # reorder x using priority

    def get(self):
        return heapq.heappop(self.queue)[1]  # pop out the smallest item

    def enumerate(self):
        return self.queue

    def check_remove(self, item):
        for (p, x) in self.queue:
            if item == x:
                self.queue.remove((p, x))

    def top_key(self):
        return self.queue[0][0]


# class QueuePrior:
#     """
#     Class: QueuePrior
#     Description: QueuePrior reorders elements using value [priority]
#     """

#     def __init__(self):
#         self.queue = []

#     def empty(self):
#         return len(self.queue) == 0

#     def put(self, item, priority):
#         count = 0
#         for (p, x) in self.queue:
#             if x == item:
#                 self.queue[count] = (priority, item)
#                 break
#             count += 1
#         if count == len(self.queue):
#             heapq.heappush(self.queue, (priority, item))  # reorder x using priority

#     def get(self):
#         return heapq.heappop(self.queue)[1]  # pop out the smallest item

#     def enumerate(self):
#         return self.queue

#     def check_remove(self, item):
#         for (p, x) in self.queue:
#             if item == x:
#                 self.queue.remove((p, x))

#     def top_key(self):
#         return self.queue[0][0]