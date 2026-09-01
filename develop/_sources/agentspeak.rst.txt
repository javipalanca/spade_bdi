=======================
The AgentSpeak language
=======================

The AgentSpeak language is a logic programming language based on the Belief-Desire-Intention (BDI) model.
It is based on the ``agentspeak`` package, which is a Python implementation of the Jason language.
The language is described in the following paper:

    ``Rao, A. S., & Georgeff, M. P. (1995). BDI agents: From theory to practice. ICMAS.``
    ``https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf_``


This section provides an overview of its syntax and semantics, focusing on how beliefs, desires, and goals are
represented and managed in AgentSpeak.

Basic Semantics
===============

- **Beliefs**: In AgentSpeak, beliefs represent the agent's knowledge about the world, itself, and other agents. They are often expressed in a simple predicate form. For example, ``is_hot(temperature)`` might represent the belief that the temperature is hot.
- **Desires and Goals**: Desires or goals are states or conditions that the agent aims to bring about. In AgentSpeak, these are often represented as special kinds of beliefs or through goal operators. For instance, ``!find_shade`` could be a goal to find shade.
- **Plans and Actions**: Plans are sequences of actions or steps that an agent will execute to achieve its goals. Actions can be internal (changing beliefs or goals) or external (interacting with the environment).

Syntax of AgentSpeak
====================

AgentSpeak is a logic-based programming language used for creating intelligent agents in multi-agent systems. Understanding its syntax is crucial for effectively programming these agents. This section provides an overview of the key syntactic elements of AgentSpeak.

Basic Elements

- **Beliefs:**
    - Syntax: ``belief(arguments)``.
    - Description: Represent the agent's knowledge or information about the world.
    - Example: ``is_sunny(true), temperature(25)``.
- **Goals:**
    - Syntax: ``!goal(arguments)``.
    - Description: Goals are states or outcomes the agent wants to bring about or information it seeks.
    - Example: ``!find_shelter``.
- **Plans:**
    - Syntax: ``TriggeringEvent : Context <- Body.``
    - Triggering Event: An event that initiates the plan, such as the addition (+) or deletion (-) of a belief or goal.
    - Context: A logical condition that must hold for the plan to be applicable.
    - Body: A sequence of actions or subgoals to be executed.
    - Example: ``+is_raining : is_outside <- !find_umbrella; .print("Hello world").``
- **Actions**
        - Syntax: ``.internal_action(arguments)``.
        - Description: Defined by the developer or the environment.
        - Example: ``.print("Hello World")``.

- **Communication**
    - Sending Messages:
        - Syntax: ``.send(receiver, illocution, content)``.
        - Illocutions: Include tell, achieve, askHow, etc.
        - Example: ``.send(agentB, tell, is_sunny(true))``.

- **Comments**
    - Single Line Comment: // This is a comment
    - Multi-Line Comment: Not typically supported in standard AgentSpeak.


Creating Agents: Beliefs, Desires, and Goals
============================================

Agents are defined by their belief base, goal base, and plan library.

- Example of Beliefs::

    is_sunny.
    temperature(high).


This represents beliefs that it is sunny and the temperature is high.

- Example of Goals::

    !stay_cool.
    !drink_water.


These are goals to stay cool and to drink water.

- Plans and Actions

A plan in AgentSpeak is a rule that specifies what to do in a given context.
Example of a Plan::


    +!stay_cool : is_sunny & temperature(high) <-
        !find_shade;
        !drink_water.


This plan states that to achieve the goal ``stay_cool``, if it is sunny and the temperature is high
(``is_sunny & temperature(high)``), the agent should achive goals ``!find_shade`` and ``!drink_water`` sequentially.

Optionally, a plan may have a custom a name that is set with a tag beginning with a @. Example::

    @my_custom_plan
    +!stay_cool : is_sunny & temperature(high) <-
        !find_shade;
        !drink_water.

Practical Implications
======================

Understanding these basic concepts is crucial for effectively programming in AgentSpeak.
``spade_bdi`` provides additional constructs and features, enhancing the basic capabilities of AgentSpeak.
When designing agents in SPADE, it is essential to carefully consider the initial set of beliefs and goals, as they drive the agent's behavior through the plans.
By grasping these fundamental concepts of AgentSpeak, developers can begin to design and implement sophisticated agents in SPADE, capable of complex decision-making and interactions in dynamic environments.
The simplicity of AgentSpeak's syntax, combined with its powerful representational capabilities, makes it a suitable choice for a wide range of applications in multi-agent systems.


Variables and the '?' Operator in AgentSpeak
--------------------------------------------

In AgentSpeak, variables are essential for dynamic information processing within an agent's logic.
They are uniquely identified by starting with an uppercase letter, distinguishing them from constants and predicates. This section delves into the syntax and use of variables, focusing on the ``?`` operator for retrieving belief values.


Syntax of Variables in AgentSpeak
=================================

**Uppercase Naming**: Variables in AgentSpeak are always denoted by names starting with an uppercase letter. This convention distinguishes them from other elements like predicates or constants.
Example of Variable Declaration: ``Location, Temp, X, Y``

Using the ``'?'`` Operator to Retrieve Belief Values
----------------------------------------------------

- **Purpose**: The ``?`` operator in AgentSpeak is used to bind the current value of a belief to a variable. This operation is akin to querying the agent's belief base.
- **Syntax**: To use the ``?`` operator, include it before the belief name and specify the variable in the belief's argument list. The format is typically ``?Belief(Variable)``.
- **Example**: If an agent has a belief ``location(office)``, and you want to bind the value office to a variable ``CurrentLocation``, you would use the statement ``?location(CurrentLocation)``.

Practical Application of Variables
==================================

    * Retrieving and Using Belief Values:

Variables are particularly useful for capturing and utilizing the values of beliefs in plans and decision-making. Example::

    +!check_current_location
    : location(CurrentLocation) & CurrentLocation == "office" <-
    .print("The agent is currently in the office").


Here, ``CurrentLocation`` is a variable that retrieves the value from the location belief.

    * Dynamic Decision-Making in Contexts:

Variables enable plans to adapt their behavior based on the changing state of the world, as represented by the agent's beliefs. Example::

    +temperature(Temp) : Temp > 30 <-
        .print("It's currently hot outside").

In this example, Temp is a variable that holds the current value of the temperature belief, triggering the plan if Temp exceeds 30.

Conclusion
----------

Proper use of variables and the ``?`` operator in AgentSpeak is fundamental for creating dynamic and responsive agents.
Variables, identified by their uppercase starting letter, offer a way to handle changing information and make context-sensitive decisions.
The ``?`` operator is a key tool for querying and utilizing the agent's belief base, enhancing the agent's ability to interact intelligently with its environment.
