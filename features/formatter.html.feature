@sequential
Feature: HTML Formatter

    In order to export behave results
    As a tester
    I want that behave generates test run data in HTML format.


    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass

            @step('a step fails')
            def step_fails(context):
                assert False, "XFAIL-STEP"

            @step('a step with parameter "{param:w}" passes')
            def step_with_one_param_passes(context, param):
                pass

            @step('a step with parameter "{param1:w}" and parameter "{param2:w}" passes')
            def step_with_two_params_passes(context, param1, param2):
                pass
            """

    Scenario: Use HTML formatter on feature without scenarios
        Given a file named "features/feature_without_scenarios.feature" with:
            """
            Feature: Simple, empty Feature
            """
        When I run "behave -f html features/feature_without_scenarios.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <h2>
                <span class="val">Feature: Simple, empty Feature</span>
              </h2>
            </div>
            """

    Scenario: Use HTML formatter on feature with description
        Given a file named "features/feature_with_description.feature" with:
            """
            Feature: Simple feature with description

                First feature description line.
                Second feature description line.

                Third feature description line (following an empty line).
            """
        When I run "behave -f html features/feature_with_description.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <h2>
                <span class="val">Feature: Simple feature with description</span>
              </h2>
              <pre class="message">First feature description line.
              Second feature description line.
              Third feature description line (following an empty line).</pre>
            </div>
            """

    Scenario: Use HTML formatter on feature with tags
        Given a file named "features/feature_with_tags.feature" with:
            """
            @foo @bar
            Feature: Simple feature with tags
            """
        When I run "behave -f html features/feature_with_tags.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <span class="tag">@foo, @bar</span>
              <h2>
                <span class="val">Feature: Simple feature with tags</span>
              </h2>
            </div>
            """

    Scenario: Use HTML formatter on feature with one empty scenario
        Given a file named "features/feature_one_empty_scenario.feature" with:
            """
            Feature:
              Scenario: Simple scenario without steps
            """
        When I run "behave -f html features/feature_one_empty_scenario.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <h2>
                <span class="val">Feature: </span>
              </h2>
            </div>
            <div class="scenario">
              <span class="scenario_file">features/feature_one_empty_scenario.feature:2</span>
              <h3 onclick="Collapsible_toggle('scenario_0')">
                <span class="val">Scenario: Simple scenario without steps</span>
              </h3>
              <ol class="scenario_steps" id="scenario_0"/>
            </div>
            """

    Scenario: Use HTML formatter on feature with one empty scenario and description
        Given a file named "features/feature_one_empty_scenario_with_description.feature" with:
            """
            Feature:
              Scenario: Simple scenario with description but without steps
                First scenario description line.
                Second scenario description line.

                Third scenario description line (after an empty line).
            """
        When I run "behave -f html features/feature_one_empty_scenario_with_description.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <h2>
                <span class="val">Feature: </span>
              </h2>
            </div>
            <div class="scenario">
              <span class="scenario_file">features/feature_one_empty_scenario_with_description.feature:2</span>
              <h3 onclick="Collapsible_toggle('scenario_0')">
                <span class="val">Scenario: Simple scenario with description but without steps</span>
              </h3>
              <pre class="message">First scenario description line.
              Second scenario description line.
              Third scenario description line (after an empty line).</pre>
              <ol class="scenario_steps" id="scenario_0"/>
            </div>
            """

    Scenario: Use HTML formatter on feature with one empty scenario and tags
        Given a file named "features/feature_one_empty_scenario_with_tags.feature" with:
            """
            Feature:
              @foo @bar
              Scenario: Simple scenario with tags but without steps
            """
        When I run "behave -f html features/feature_one_empty_scenario_with_tags.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <h2>
                <span class="val">Feature: </span>
              </h2>
            </div>
            <div class="scenario">
              <span class="scenario_file">features/feature_one_empty_scenario_with_tags.feature:3</span>
              <span class="tag">@foo, @bar</span>
              <h3 onclick="Collapsible_toggle('scenario_0')">
                <span class="val">Scenario: Simple scenario with tags but without steps</span>
              </h3>
              <ol class="scenario_steps" id="scenario_0"/>
            </div>
            """

    Scenario: Use HTML formatter on feature with one passing scenario
        Given a file named "features/feature_one_passing_scenario.feature" with:
            """
            Feature:
              Scenario: Simple scenario with passing steps
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step passes
            """
        When I run "behave -f html features/feature_one_passing_scenario.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <h2>
                <span class="val">Feature: </span>
              </h2>
            </div>
            <div class="scenario">
              <span class="scenario_file">features/feature_one_passing_scenario.feature:2</span>
              <h3 onclick="Collapsible_toggle('scenario_0')">
                <span class="val">Scenario: Simple scenario with passing steps</span>
              </h3>
              <ol class="scenario_steps" id="scenario_0">
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Given </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">When </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Then </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">And </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">But </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
              </ol>
            </div>
            """

    Scenario: Use HTML formatter on feature with one failing scenario
        Given a file named "features/feature_one_failing_scenario.feature" with:
            """
            Feature:
              Scenario: Simple scenario with failing step
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step fails
            """
        When I run "behave -f html features/feature_one_failing_scenario.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            0 scenarios passed, 1 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <h2>
                <span class="val">Feature: </span>
              </h2>
            </div>
            <div class="scenario">
              <span class="scenario_file">features/feature_one_failing_scenario.feature:2</span>
              <h3 onclick="Collapsible_toggle('scenario_0')" style="background: #C40D0D; color: #FFFFFF">
                <span class="val">Scenario: Simple scenario with failing step</span>
              </h3>
              <ol class="scenario_steps" id="scenario_0">
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Given </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">When </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Then </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">And </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step failed">
                  <div class="step_name">
                    <span class="keyword">But </span>
                    <span class="step val">a step fails</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:7</span>
                  </div>
                  <span class="embed"/>
                  <a class="message" onclick="Collapsible_toggle('embed_1')">Error message</a>
                  <pre id="embed_1" style="display: none; white-space: pre-wrap;">Assertion Failed: XFAIL-STEP</pre>

                </li>
              </ol>
            </div>
            """

    Scenario: Use HTML formatter on feature with one scenario with skipped steps
        Given a file named "features/feature_one_failing_scenario_with_skipped_steps.feature" with:
            """
            Feature:
              Scenario: Simple scenario with failing and skipped steps
                  Given a step passes
                  When a step fails
                  Then a step passes
                  And a step passes
                  But a step passes
            """
        When I run "behave -f html features/feature_one_failing_scenario_with_skipped_steps.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            0 scenarios passed, 1 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="feature">
              <h2>
                <span class="val">Feature: </span>
              </h2>
            </div>
            <div class="scenario">
              <span class="scenario_file">features/feature_one_failing_scenario_with_skipped_steps.feature:2</span>
              <h3 onclick="Collapsible_toggle('scenario_0')" style="background: #C40D0D; color: #FFFFFF">
                <span class="val">Scenario: Simple scenario with failing and skipped steps</span>
              </h3>
              <ol class="scenario_steps" id="scenario_0">
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Given </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step failed">
                  <div class="step_name">
                    <span class="keyword">When </span>
                    <span class="step val">a step fails</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:7</span>
                  </div>
                  <span class="embed"/>
                  <a class="message" onclick="Collapsible_toggle('embed_1')">Error message</a>
                  <pre id="embed_1" style="display: none; white-space: pre-wrap;">Assertion Failed: XFAIL-STEP</pre>
                </li>
              </ol>
            </div>
            """

    Scenario: Use HTML formatter on feature with three scenarios
        Given a file named "features/feature_three_scenarios.feature" with:
            """
            Feature: Many Scenarios
              Scenario: Passing
                  Given a step passes
                  Then a step passes

              Scenario: Failing
                  Given a step passes
                  Then a step fails

              Scenario: Failing with skipped steps
                  Given a step passes
                  When a step fails
                  Then a step passes
            """
        When I run "behave -f html features/feature_three_scenarios.feature"
        Then it should fail with:
            """
            0 features passed, 1 failed, 0 skipped
            1 scenario passed, 2 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="scenario">
              <span class="scenario_file">features/feature_three_scenarios.feature:2</span>
              <h3 onclick="Collapsible_toggle('scenario_0')">
                <span class="val">Scenario: Passing</span>
              </h3>
              <ol class="scenario_steps" id="scenario_0">
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Given </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Then </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
              </ol>
            </div>
            <div class="scenario">
              <span class="scenario_file">features/feature_three_scenarios.feature:6</span>
              <h3 onclick="Collapsible_toggle('scenario_1')" style="background: #C40D0D; color: #FFFFFF">
                <span class="val">Scenario: Failing</span>
              </h3>
              <ol class="scenario_steps" id="scenario_1">
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Given </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step failed">
                  <div class="step_name">
                    <span class="keyword">Then </span>
                    <span class="step val">a step fails</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:7</span>
                  </div>
                  <span class="embed"/>
                  <a class="message" onclick="Collapsible_toggle('embed_1')">Error message</a>
                  <pre id="embed_1" style="display: none; white-space: pre-wrap;">Assertion Failed: XFAIL-STEP</pre>

                </li>
              </ol>
            </div>
            <div class="scenario">
              <span class="scenario_file">features/feature_three_scenarios.feature:10</span>
              <h3 onclick="Collapsible_toggle('scenario_2')" style="background: #C40D0D; color: #FFFFFF">
                <span class="val">Scenario: Failing with skipped steps</span>
              </h3>
              <ol class="scenario_steps" id="scenario_2">
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Given </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step failed">
                  <div class="step_name">
                    <span class="keyword">When </span>
                    <span class="step val">a step fails</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:7</span>
                  </div>
                  <span class="embed"/>
                  <a class="message" onclick="Collapsible_toggle('embed_2')">Error message</a>
                  <pre id="embed_2" style="display: none; white-space: pre-wrap;">Assertion Failed: XFAIL-STEP</pre>

                </li>
              </ol>
            </div>
            """

    Scenario: Use HTML formatter on step with one parameter
        Given a file named "features/feature_step_with_one_parameter.feature" with:
            """
            Feature:
              Scenario: Simple scenario with one parameter in step
                  Given a step passes
                  When a step with parameter "foo" passes
                  Then a step passes
            """
        When I run "behave -f html features/feature_step_with_one_parameter.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="scenario">
              <span class="scenario_file">features/feature_step_with_one_parameter.feature:2</span>
                <h3 onclick="Collapsible_toggle('scenario_0')">
                  <span class="val">Scenario: Simple scenario with one parameter in step</span>
                </h3>
              <ol class="scenario_steps" id="scenario_0">
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Given </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">When </span>
                    <span class="step val">
                      a step with parameter &quot;
                      <b>foo</b>
                    </span>
                    <span class="step val">&quot; passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:11</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Then </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
              </ol>
            </div>
            """

    Scenario: Use HTML formatter on step with several parameters
        Given a file named "features/feature_step_with_parameters.feature" with:
            """
            Feature:
              Scenario: Simple scenario with parameters in step
                  Given a step passes
                  When a step with parameter "foo" and parameter "bar" passes
                  Then a step passes
            """
        When I run "behave -f html features/feature_step_with_parameters.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <div class="scenario">
              <span class="scenario_file">features/feature_step_with_parameters.feature:2</span>
              <h3 onclick="Collapsible_toggle('scenario_0')">
                <span class="val">Scenario: Simple scenario with parameters in step</span>
              </h3>
              <ol class="scenario_steps" id="scenario_0">
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Given </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">When </span>
                    <span class="step val">
                      a step with parameter &quot;
                      <b>foo</b>
                    </span>
                    <span class="step val">
                      &quot; and parameter &quot;
                      <b>bar</b>
                    </span>
                    <span class="step val">&quot; passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:15</span>
                  </div>
                  <span class="embed"/>
                </li>
                <li class="step passed">
                  <div class="step_name">
                    <span class="keyword">Then </span>
                    <span class="step val">a step passes</span>
                  </div>
                  <div class="step_file">
                    <span>features/steps/steps.py:3</span>
                  </div>
                  <span class="embed"/>
                </li>
              </ol>
            </div>
            """

    Scenario: Use HTML formatter on step with multiline
        Given a file named "features/feature_multiline_step.feature" with:
            """
            Feature:
              Scenario: Simple scenario with multiline string in step
                Given a step passes
                When a step passes:
                  '''
                  Tiger, tiger, burning bright
                  In the forests of the night,
                  What immortal hand or eye
                  Could frame thy fearful symmetry?
                  '''
                Then a step passes
            """
        When I run "behave -f html features/feature_multiline_step.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <li class="step passed">
              <div class="step_name">
                <span class="keyword">When </span>
                <span class="step val">a step passes</span>
              </div>
              <div class="step_file">
                <span>features/steps/steps.py:3</span>
              </div>
              <span class="embed"/>
              <div class="message">
                <pre style="white-space: pre-wrap;">Tiger, tiger, burning bright
                In the forests of the night,
                What immortal hand or eye
                Could frame thy fearful symmetry?</pre>
              </div>
            </li>
            """

    Scenario: Use HTML formatter on step with table
        Given a file named "features/feature_step_with_table.feature" with:
            """
            Feature: Step with table data
              Scenario:
                Given a step passes
                When a step passes:
                  | Name | Value |
                  | Foo  | 42    |
                  | Bar  | qux   |
                Then a step passes
            """
        When I run "behave -f html features/feature_step_with_table.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            <li class="step passed">
              <div class="step_name">
                <span class="keyword">When </span>
                <span class="step val">a step passes</span>
              </div>
              <div class="step_file">
                <span>features/steps/steps.py:3</span>
              </div>
              <span class="embed"/>
              <table>
                <tr>
                  <th>Name</th>
                  <th>Value</th>
                </tr>
                <tr>
                  <td>Foo</td>
                  <td>42</td>
                </tr>
                <tr>
                  <td>Bar</td>
                  <td>qux</td>
                </tr>
              </table>
            </li>
            """
