
===================================
Create custom actions and functions
===================================

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



