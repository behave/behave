======
behave-parallel
======
The real devs are at the following https://github.com/behave/behave

Ruby has rspec/cucumber for BDD, and Ruby has parallel_tests to run them in parallel
Python have behave and lettuce, but nothing to run python-BDD-tests in parallel.
So I modded behave to do it.

======
USAGE
======::
	behave --threads 4

======
Experimental
======
So I'm sure you can imagine the things that could happen by turning a serial process into a parallel one.
So far, this seems to work for me. Your milage may vary.


======
Known issues
======
1) I broke ALL THE THINGS.
Specifically, do not try to use the logging, junit, formatting or capture related flags when using --threads.
Best case they just don't work. Worse case, they randomly fail in some mysterious and spectacular way.
the -t, -k and -e flags seem to be working so that's cool. ^_^

2) The global context object is NOT THREAD SAFE!
I've tried using modifying the context object from threads. You get wierd errors like "Context has no attribute myvar" when
I know for sure it was assigned before the code got there. probably was in the middle of being re-assigned by another
thread; I don't know. But if you need that kind of access to the context object, I recommend using locks. e.g.

--- environment.py ---::
  def before_all(context):
	import threading
	context.lock = threading.Lock()
	context.counter = 0

Then in your steps code::
	context.lock.acquire()
	context.counter += 1
	context.lock.release()

Something like that.


I don't know if I'll be able to fix any issues anyone opens against this repo.
I can't even believe I managed to get this working at all. o_O;


