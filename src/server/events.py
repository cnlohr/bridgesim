#! /usr/bin/python3
import heapq
import inspect
import threading
import time

class EventQueue:
  def __init__(self, items=None):
    if items is None:
      self.items = []
    else:
      self.items = list(items)
      heapq.heapify(self.items)
  def add(self, *items):
    """Add items to this event queue, respecting the order."""
    if len(items) < 10:
      for item in items:
        heapq.heappush(self.items, item)
    else:
      newitems = list(items)
      heapq.heapify(newitems)
      self.items = list(heapq.merge(self.items, newitems))
  def top(self):
    return self.items[0]
  def __len__(self):
    return len(self.items)
  def pop(self):
    """Remove and return the next-smallest item from this queue."""
    return heapq.heappop(self.items)

class Event:
  def __init__(self, callback, next_due, callback_args = [], repeat_interval = None, repeat_count = 1):
    assert (inspect.getargspec(callback).varargs is None) and \
            len(inspect.getargspec(callback).args) == len(callback_args) or \
            len(inspect.getargspec(callback).args) <= len(callback_args), "Wrong number of arguments for callback passed"
    self.callback = callback
    self.callback_args = callback_args
    self.next_due = next_due
    self.repeat_interval = repeat_interval
    self.repeat_count = repeat_count
  def execute(self):
    self.callback(*self.callback_args)
    if self.repeat_count > 0:
      self.next_due = self.next_due + self.repeat_interval
      self.repeat_count -= 1
  def __cmp__(self, other):
    if not isinstance(other, Event):
      raise TypeError("Cannot compare %s to %s" % (self, other))
    return cmp(self.next_due, other.next_due)

class QueueExecutor:
  @classmethod
  def executeEvents(cls, self):
    q = self.q
    waiter = self.waiter
    try:
      while self.go:
        now = time.time()
        if len(q) == 0:
          waitInterval = 0
        else:
          while len(q) != 0:
            waitInterval = q.top().next_due - now
            if waitInterval > 0: break
            event = q.pop()
            event.execute()
            if event.repeat_count > 0:
              q.add(event)
        self.waitingUntil = now + waitInterval
        waiter.wait(timeout=waitInterval)
    except KeyboardInterrupt:
      print("Got KeyboardInterrupt")
      return
  
  def __init__(self, items = None):
    if items is None:
      self.q = EventQueue()
    else:
      self.q = EventQueue(items)
    self.thread = threading.Thread(target=QueueExecutor.executeEvents, args=(self,))
    self.go = True
    self.waiter = threading.Event()
    self.thread.start()
  def addEvent(self, callback, next_due, repeat_interval = None, repeat_count = 1, *args):      
    self.q.add(Event(callback, next_due, args, repeat_interval, repeat_count))
    if next_due < time.time():
      # Wake up, execution thread, this one's late!
      self.waiter.set()
  def stop(self):
    self.go = False
    self.waiter.set()