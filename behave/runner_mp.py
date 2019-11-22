# -*- coding: UTF-8 -*-
"""
This module provides multiprocessing Runner class.
"""

import six
import os
import multiprocessing

from behave.formatter._registry import make_formatters
from behave.runner import Runner, Context
from behave.model import Feature, Scenario, ScenarioOutline, NoMatch
from behave.runner_util import parse_features, load_step_modules
from behave.step_registry import registry as the_step_registry

if six.PY2:
    import Queue as queue
else:
    import queue


class MultiProcRunner(Runner):
    """Master multiprocessing runner: scans jobs and distributes to slaves

        This runner should not do any "processing" tasks, apart from scanning
        the feature files and their scenarios. It then spawns processing nodes
        and lets them consume the queue of tasks scheduled.
    """
    def __init__(self, config):
        super(MultiProcRunner, self).__init__(config)
        self.jobs_map = {}
        self.jobsq = multiprocessing.JoinableQueue()
        self.resultsq = multiprocessing.Queue()
        self._reported_features = set()
        self.results_fail = False

    def run_with_paths(self):
        feature_locations = [filename for filename in self.feature_locations()
                        if not self.config.exclude(filename)]
        self.load_hooks()   # hooks themselves not used, but 'environment.py' loaded
        # step definitions are needed here for formatters only
        self.load_step_definitions()
        features = parse_features(feature_locations, language=self.config.lang)
        self.features.extend(features)
        feature_count, scenario_count = self.scan_features()
        njobs = len(self.jobs_map)
        proc_count = int(self.config.proc_count)
        print ("INFO: {0} scenario(s) and {1} feature(s) queued for"
                " consideration by {2} workers. Some may be skipped if the"
                " -t option was given..."
               .format(scenario_count, feature_count, proc_count))

        procs = []
        old_outs = self.config.outputs
        self.config.outputs = []
        old_reporters = self.config.reporters
        self.config.reporters = []

        for i in range(proc_count):
            client = MultiProcClientRunner(self, i)
            p = multiprocessing.Process(target=client.run)
            procs.append(p)
            p.start()
            del p

        print ("INFO: started {0} workers for {1} jobs.".format(proc_count, njobs))

        self.config.reporters = old_reporters
        self.formatters = make_formatters(self.config, old_outs)
        self.config.outputs = old_outs
        while (not self.jobsq.empty()):
            # 1: consume while tests are running
            self.consume_results()
            if not any([p.is_alive() for p in procs]):
                break

        if any([p.is_alive() for p in procs]):
            self.jobsq.join()   # wait for all jobs to be processed
            print ("INFO: all jobs have been processed")

            while self.consume_results(timeout=0.1):
                # 2: remaining results
                pass

            # then, wait for all workers to exit:
            [p.join() for p in procs]

        print ("INFO: all sub-processes have returned")

        while self.consume_results(timeout=0.1):
            # 3: just in case some arrive late in the pipe
            pass

        for f in self.features:
            # make sure all features (including ones that have not returned)
            # are printed
            self._output_feature(f)

        for formatter in self.formatters:
            formatter.close()
        for reporter in self.config.reporters:
            reporter.end()

        return self.results_fail

    def scan_features(self):
        raise NotImplementedError

    def consume_results(self, timeout=1):
        try:
            job_id, result = self.resultsq.get(timeout=timeout)
        except queue.Empty:
            return False

        if job_id is None and result == 'set_fail':
            self.results_fail = True
            return True

        item = self.jobs_map.get(job_id)
        if item is None:
            print("ERROR: job_id=%x not found in master map" % job_id)
            return True

        try:
            item.recv_status(result)
            if isinstance(item, Feature):
                self._output_feature(item)
            elif isinstance(item, Scenario):
                feature = item.feature
                print("INFO: scenario finished: %s %s" % (item.name, item.status))
                if feature.is_finished:
                    self._output_feature(feature)
        except Exception as e:
            print("ERROR: cannot receive status for %r: %s" % (item, e))
            if self.config.wip and not self.config.quiet:
                import traceback
                traceback.print_exc()
        return True

    def _output_feature(self, feature):
        if id(feature) in self._reported_features:
            return
        self._reported_features.add(id(feature))

        def _out_scenario(scenario, formatter):
            formatter.scenario(scenario)
            for step in scenario.steps:
                formatter.step(step)
            for step in scenario.steps:
                match = the_step_registry.find_match(step)
                if match:
                    formatter.match(match)
                else:
                    formatter.match(NoMatch())
                formatter.result(step)

        for formatter in self.formatters:
            formatter.uri(feature.filename)
            formatter.feature(feature)
            if feature.background:
                formatter.background(feature.background)
            for scenario in feature.scenarios:
                if isinstance(scenario, ScenarioOutline):
                    for scen in scenario.scenarios:
                        _out_scenario(scen, formatter)
                else:
                    _out_scenario(scenario, formatter)


            formatter.eof()

        for reporter in self.config.reporters:
            reporter.feature(feature)


class MultiProcRunner_Feature(MultiProcRunner):
    def scan_features(self):
        for feature in self.features:
            self.jobs_map[id(feature)] = feature
            self.jobsq.put(id(feature))
            for scen in feature.scenarios:
                scen.background_steps
                if isinstance(scen, ScenarioOutline):
                    # compute the sub-scenarios before serializing
                    for subscen in scen.scenarios:
                        subscen.background_steps

        return len(self.jobs_map), 0


class MultiProcRunner_Scenario(MultiProcRunner):
    def scan_features(self):
        nfeat = nscens = 0
        def put(sth):
            idf = id(sth)
            self.jobs_map[idf] = sth
            self.jobsq.put(idf)

        for feature in self.features:
            if 'serial' in feature.tags:
                put(feature)
                nfeat += 1
                for scen in feature.scenarios:
                    scen.background_steps
                    if isinstance(scen, ScenarioOutline):
                        # compute the sub-scenarios before serializing
                        for subscen in scen.scenarios:
                            subscen.background_steps
                continue
            for scenario in feature.scenarios:
                scenario.background_steps  # compute them, before sending out
                if scenario.type == 'scenario':
                    put(scenario)
                    nscens += 1
                else:
                    for subscenario in scenario.scenarios:
                        subscenario.background_steps
                        put(subscenario)
                        nscens += 1

        return nfeat, nscens


class MultiProcClientRunner(Runner):
    """Multiprocessing Client runner: picks "jobs" from parent queue

        Each client is tagged with a `num` to appear in outputs etc.
    """
    def __init__(self, parent, num):
        super(MultiProcClientRunner, self).__init__(parent.config)
        self.num = num
        self.jobs_map = parent.jobs_map
        self.jobsq = parent.jobsq
        self.resultsq = parent.resultsq

    def iter_queue(self):
        """Iterator fetching features from the queue

            Note that this iterator is lazy and multiprocess-affected:
            it cannot know its set of features in advance, will dynamically
            yield ones as found in the queue
        """
        while True:
            try:
                job_id = self.jobsq.get(timeout=0.5)
            except queue.Empty:
                break

            job = self.jobs_map.get(job_id, None)
            if job is None:
                print("ERROR: missing job id=%s from map" % job_id)
                self.jobsq.task_done()
                continue

            if isinstance(job, Feature):
                yield job
                try:
                    self.resultsq.put((job_id, job.send_status()))
                except Exception as e:
                    print("ERROR: cannot send result: {0}".format(e))
            elif isinstance(job, Scenario):
                # construct a dummy feature, having only this scenario
                kwargs = {}
                for k in ('filename', 'line', 'keyword', 'name', 'tags',
                          'description', 'background', 'language'):
                    kwargs[k] = getattr(job.feature, k)
                kwargs['scenarios'] = [job]
                orig_parser = job.feature.parser
                feature = Feature(**kwargs)
                feature.parser = orig_parser
                yield feature
                try:
                    self.resultsq.put((job_id, job.send_status()))
                except Exception as e:
                    print("ERROR: cannot send result: {0}".format(e))
            else:
                raise TypeError("Don't know how to process: %s" % type(job))
            self.jobsq.task_done()

    def run_with_paths(self):
        self.context = Context(self)
        self.load_hooks()
        self.load_step_definitions()
        assert not self.aborted

        failed = self.run_model(features=self.iter_queue())
        if failed:
            self.resultsq.put((None, 'set_fail'))
        self.resultsq.close()


# eof
