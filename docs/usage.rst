=====
Usage
=====

The agentspeak language
-----------------------

The agentspeak language is a logic programming language based on the Belief-Desire-Intention (BDI) model.
It is based on the ``agentspeak`` package, which is a Python implementation of the Jason language.
The language is described in the following paper:

    ``Rao, A. S., & Georgeff, M. P. (1995). BDI agents: From theory to practice. ICMAS.``
    `https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf`_

The syntax of the language is as follows:

        * ``+``: belief
        * ``-``: remove belief
        * ``!``: goal
        * ``?``: test goal
        * ``@``: maintenance goal
        * ``<-``: plan
        * ``:``: conditional plan
        * ``.``: internal action


Where a belief is a logical formula, a goal is a logical formula or a plan, a plan is a sequence of actions, and an action is a function call.
Example::

        // Creating a belief
        +operation(sum)
        // Creating a goal
        !start
        // Creating a plan
        +!start <- .my_action(2)
        // Creating a plan with a conditional
        +!start: operation(pow)  <- .my_action(4)


Create custom internal actions and functions
--------------------------------------------

You must to overload the ``add_custom_actions`` method and to use the ``add_function`` or ``add`` (for actions) decorator.
This custom method receives always the ``actions`` parameter::

    import spade_bdi

    class MyCustomBDIAgent(BDIAgent):

        def add_custom_actions(self, actions):
            @actions.add_function(".my_function", (int,))
            def _my_function(x):
                return x * x

            @actions.add(".my_action", 1)
            def _my_action(agent, term, intention):
                arg = agentspeak.grounded(term.args[0], intention.scope)
                print(arg)
                yield




.. hint:: Adding a function requires to call the ``add_function`` decorator with two parameters: the name of the function (starting with a dot)
          and a tuple with the types of the parameters (e.g. ``(int, str)``).

.. hint:: Adding an action requires to call the ``add`` decorator with two parameters: the name of the action (starting with a dot)
          and the number of parameters. Also, the method being decorated receives three parameters: ``agent``, ``term,`` and ``intention``.

