======
behave-parallel
======

The real devs are at the following https://github.com/behave/behave


Ruby has rspec/cucumber for BDD, and Ruby has parallel_tests to run them in parallel.
Python has pyvows and pycuracy, but they're not exactly what I'm looking for.
=======
The real developers, and core documentation, are at https://github.com/behave/behave


Ruby has rspec/cucumber for BDD, and Ruby has parallel_tests to run them in parallel.
Python has pyvows, lettuce and pycuracy, but they're not exactly what I'm looking for.
I feel that behave is the most advanced BDD framework for python, so giving it parallel powers seemed ideal.


======
Why is this better than other python BDD test frameworks?
======

Maybe it's not, but it serves a need I have at the moment. I've looked at the other ones and while they are great - they don't exactly do what I want. Here is what I think makes behave-parallel different from the rest:

* BDD, free-form sentences with the only requirement of starting with words like given, then, etc.
* .feature files that are completely seperate from the actual implementation code.
* Parallelism

To that end, lettuce, pyVows, nosetest's BDD plugin and pyccuracy seem to be the top 4. You might consider the following points trivial, as they may well be, but for my specific needs these made a difference.

* Lettuce and behave seem about equal; but I get the impression that there's more support around behave. Also, behave seems to have more options than lettuce(compare their "-h" output). I particularly enjoy behave's -i and -e options. Also note that the lack of tags in lettuce(as of this writing) is a significant issue for me.
* pyVows is cool, but no .feature file. I particularly enjoy the fact that I can email a .feature to an entire project-team, technical or non-techie, and all of them can understand it. Even more awesome is the fact they can even change the feature file to change the code since parts of the sentence can be substituded into the actual python code that it's tied to. e.g., "Then I sleep for 20 seconds." If someone wants to make it 30 seconds, they change the sentence and the code will do it - they didn't actually need to know any code.
* nosetest's BDD doesn't have a .feature file for clear reability without knowing code.
* pyccuracy has BDD, parallelism and plain english scenarios - but, it is very one-to-one match. Exactly 1 sentence to 1 action; and a very specific structured sentence at that. This does not work for me because I am doing very custom tests against mobile devices and require flexibility in my selenium commands - even custom commands that are not part of selenium, e.g. https://gist.github.com/tokunbo/4747316 . Also, I don't want 1 sentence per command. I want to say "Delete Remote object" and have it tied to a function that does whatever it must to meet that requirement. Making the .feature file easy to read without the complexity of the exact steps needed to do it.
* One more thing. I've just been informed of https://github.com/griddynamics/bunch/. Allowing parallelism of lettuce tests. That is very, very close to what behave-parallel brings to the table.I was a bit hopeful, but it doesn't seem maintained anymore. The links to docs gives me a 404 and trying to run the examples test error with a FileNotFound exception. So I don't know if lettuce+bunch work at all anymore or what's going on there. If the documented test-examples worked, then maybe I could evaluate it and use it.
So there you go. If you don't agree with what I said above, feel free to use the others. I just did this as yet another option for test-developers and it meets 100% of what I, and the rest of the team, are looking for at this exact moment.



======
USAGE
======

	behave --processes 4 --parallel-element scenario


Just like RSpec's parallel_test, and python's nosetests, it's up to you to decide a sane value for the number of pids that should be created for your parallel running tests. Another option, --parallel-element must go with it. The 2 valid values are 'scenario' or 'feature'. If you don't give --parallel-element, it'll be assumed you wanted 'scenario'.

======
Here's how it works:
======

* If you had 3 features, each with 3 scenarios, that's 9 scenarios total. So, if you ran _behave --processes 9 --parallel-element scenario_, first behave will find the 9 scenarios then create 9 pids to run each of them *at the same time*.
* If you ran _behave --processes 9 --parallel-element feature_, then the 3 features will be queued for processing by 9 pids. Since there are only 3 features, 3 pids will each get a feature, the other 6 pids will exit because the workqueue will be empty. The 3 pids with features will begin their work at the same time; running all the scenarios with the features in order.
* Now here's where things get a bit complicated. The tag called __@serial__ on a feature will alter execution flow. If you run _behave --process 9 --parallel-element scenario_, but one of the 3 features has the @serial tag. That feature will not have its scenarios parallelized. What will happen is only 2 of the features will have the scenarios parallelized. The job queue will ultimately contain 6 scenarios and 1 feature, a total of 7 "tasks". So of the 9 pids created by --processes 9, 7 pids will get a "task" to work on and 2 pids will exit immediately since the queue will be empty for them. 6 of the seven pids will do the one scenario they're assigned to and exit, the 7th pid will run the entire feature that had the @serial tag - doing each of the scenarios in the order they appear in the .feature file.
* Finally, If a feature gets its scenarios parallelized the effect also applies to its scenario outlines. So let's say you only had 1 .feature file, with 1 scenario outline that has 10 rows in the Examples table. If you run _behave --processes 10 --parallel-element scenario_, the 10 rows of data will generate 10 scenarios and all 10 will run at the same time by the 10 pids created by --processes 10.  
* The "Background" element will run before each scenario runs, but in parallel. So if you have 2 workers and 2 scenarios in queue each worker will run its own instance of Background then run the scenario assigned to it.


If you don't give the --procceses option, then behave should work like it always did. 

Because you'd be running scenarios in parallel, it would be madness to allow all the pids to print to stdout while running. You'll just get a scrambled mess. Instead, I opted to print out the first letter of the end-status for every 'task'(be it a scenario or feature) that is completed to stderr(it's unbuffered, so it'll appear immediately) so you have at least a little idea about the progress behave is making. So "p" for passed, "f" for failed, "s" for skipped. Note that you can give --no-capture to see all the madness if you want; I don't know how that'd be helpful to you in parallel-running tests but if you want to do it, go for it.

Example output that shows up after all scenarios have been processed.

	2013-02-18 17:32:27|WORKER4 START|Scenario:Devide by num|Feature:talkingfeature_b|/home/toks/tmp3/features/talkingfeature_b.feature
	Scenario Outline: Devide by num
	       Given I decide to yell 3 ... passed
	        Then I will devide by 1 ... passed
	
	2013-02-18 17:32:29|WORKER4 END|Scenario:Devide by num|Feature:talkingfeature_b|status:passed|Duration:2.00221419334


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

======
Known issues when using --processes flag
======
I broke ALL THE THINGS!

* The -t, -k, -i, -e, --no-capture, --show-timings and --junit flags are the only ones I'm confident still work properly. Feel free to try other flags, maybe they work or maybe they don't. Maybe they fail silently in mysterious & spectacular ways. Who knows.

* I patched out the warnings that Context gives when user code overrides its context; it produced too much noise because of this whole parallel thing. It really shouldn't matter for parallelism. Since you've designed your scenarios to run in parallel you shouldn't even need to be writing anything to context that would be read by a different scenario. Set what you need by creating features/environment.py def before_all(context): and set whatever you need inside context(like say, URLs, usernames, passwords,etc). before_all(context) will run before any scenario so you can rely on that.
	 
* Since each scenario is now running in its own pid, changes that one pid makes to context won't be reflected anywhere else. Each scenario gets its own copy of the context object. Also, and this is the sad part :(, your steps will generally only be able to access python primitives in the context object. If you have one of your tests fail because of something related to python trying to call the method \__new__(), it's because you tried to move around a complex object between processes. I think the general rule is only pickle-able objects can be copied between processes. Maybe when I have freetime, I'll use SWIG to write C code manipulating pointers and create a method called context.unsafe_access_parent_copy() that'll get you a handle to the main-process version. Combined with multiprocessing.Lock, it would leave you to be a responsible test-developer in knowing all the terrible things that could go wrong with locking, unlocking and accessing a single object concurrently. Or - I'll find that it's just impossible and seriously, if you designed _concurrent_ tests that rely on sharing data you've probably done something wrong anyway. ^_^;. Keep in mind, that if you put the __@serial__ tag on a feature, that feature's scenarios will be run in order by a single pid. Therefore in that situation, if the first scenario changes something in context, it __will__ carry over to subsequent scenarios.

* I don't print out the total time behave has ran. Too lazy to code it; just use linux's "time" command.

		/usr/bin/time behave --processes 2 --parallel-element feature

* You can't use the --format flag when using parallelization. I've noticed it tends to break stuff if it's set to anything other than "plain", so now I just hardcode it to always be "plain".

======
Advice
======

Ultimately this is probably the way you want to run it most of the time:

		behave --processes 4 --parallel-element scenario --junit --show-timings --logging-level INFO





