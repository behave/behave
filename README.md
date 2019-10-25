behave-parallel
================

Q: Will this be merged upstream?

A: I'd like to, but... https://github.com/behave/behave/pull/616


USAGE
======

	behave --processes 4 --parallel-element scenario


Just like RSpec's parallel_test, and python's nosetests, it's up to you to decide a sane value for the number of pids that should be created for your parallel running tests. Another option, --parallel-element must go with it. The 2 valid values are 'scenario' or 'feature'. If you don't give --parallel-element, it'll be assumed you wanted 'scenario'.


Here's how it works:
====================

* If you had 3 features, each with 3 scenarios, that's 9 scenarios total. So, if you ran _behave --processes 9 --parallel-element scenario_, first behave will find the 9 scenarios then create 9 pids to run each of them *at the same time*.
* This implementation keeps a queue of pending jobs at the *master* process, which
each of the workers poll for tasks. Whenever a worker finishes its task (either
feature or scenario), it asks the master for the next one. This ensures that load
is distributed, even if scenarios have much different length. Example, if the test
suite has one scenario of 10min and 5 of 2min, with --processes=2, first worker
will be busy doing the 10min one and second should execute the other 5x2min in the
meanwhile. This, of course, is the best-case result, as the order of picking may be
randomized (see hashseed randomization) and, at worst case, both will finish with
all short tasks, until one will pick the 10min one late.
* Now here's where things get a bit complicated. The tag called __@serial__ on a feature will alter execution flow. If you run _behave --process 9 --parallel-element scenario_, but one of the 3 features has the @serial tag. That feature will not have its scenarios parallelized. What will happen is only 2 of the features will have the scenarios parallelized. The job queue will ultimately contain 6 scenarios and 1 feature, a total of 7 "tasks". So of the 9 pids created by --processes 9, 7 pids will get a "task" to work on and 2 pids will exit immediately since the queue will be empty for them. 6 of the seven pids will do the one scenario they're assigned to and exit, the 7th pid will run the entire feature that had the @serial tag - doing each of the scenarios in the order they appear in the .feature file.
* Finally, If a feature gets its scenarios parallelized the effect also applies to its scenario outlines. So let's say you only had 1 .feature file, with 1 scenario outline that has 10 rows in the Examples table. If you run _behave --processes 10 --parallel-element scenario_, the 10 rows of data will generate 10 scenarios and all 10 will run at the same time by the 10 pids created by --processes 10.
* The "Background" element will run before each scenario runs, but in parallel. So if you have 2 workers and 2 scenarios in queue each worker will run its own instance of Background then run the scenario assigned to it.


If you don't give the --procceses option, then behave should work like it always did.

You don't have to install this system-wide. Keep your normal offical-copy of behave. You can use this modified one without installing - but you really do have to do "pip install behave" to get the offical version because it'll install other dependencies that the official version, and this parallel-version, both need:

	$ pwd
	/home/toks
	$ git clone git@github.com:tokunbo/behave-parallel.git
	Cloning into behave-parallel...
	remote: Counting objects: 2473, done.
	remote: Compressing objects: 100% (793/793), done.
	remote: Total 2473 (delta 1759), reused 2327 (delta 1644)
	Receiving objects: 100% (2473/2473), 436.91 KiB, done.
	Resolving deltas: 100% (1759/1759), done.
	$ ./behave-parallel/bin/behave
	No steps directory in "/home/toks/features"
	$


Known issues when using --processes flag
=========================================

* Since each scenario is now running in its own pid, changes that one pid makes to context won't be reflected anywhere else. Each scenario gets its own copy of the context object. Also, and this is the sad part :(, your steps will generally only be able to access python primitives in the context object. If you have one of your tests fail because of something related to python trying to call the method \__new__(), it's because you tried to move around a complex object between processes. I think the general rule is only pickle-able objects can be copied between processes. Maybe when I have freetime, I'll use SWIG to write C code manipulating pointers and create a method called context.unsafe_access_parent_copy() that'll get you a handle to the main-process version. Combined with multiprocessing.Lock, it would leave you to be a responsible test-developer in knowing all the terrible things that could go wrong with locking, unlocking and accessing a single object concurrently. Or - I'll find that it's just impossible and seriously, if you designed _concurrent_ tests that rely on sharing data you've probably done something wrong anyway. ^_^;. Keep in mind, that if you put the __@serial__ tag on a feature, that feature's scenarios will be run in order by a single pid. Therefore in that situation, if the first scenario changes something in context, it __will__ carry over to subsequent scenarios.







