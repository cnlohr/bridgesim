#! /usr/bin/python3
import time
from events import *

def test1(foo, *args):
  print("foo: %s otherargs: %s time: %06.3f" % (foo, args, time.time() % 100))

q = QueueExecutor()

q.addEvent(test1, time.time() + 3, 1, 5, "foo", "bar", "baz")
q.addEvent(test1, time.time() + .5, .3, 20, "foo2", "bar")
print("Main thread asleep at %s" % (time.time(),))
time.sleep(6)
print("Main thread awake, terminating...")
q.stop()