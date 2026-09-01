============================
Creating Plans in AgentSpeak
============================

In AgentSpeak, plans are central to the behavior of agents. They define how an agent should react to certain events or changes in their environment or internal state.
This section explores the syntax and structure of plans in AgentSpeak, providing examples and best practices.

Plan Syntax
===========

**Basic Structure**: A plan in AgentSpeak typically consists of a triggering event, an optional context, and a sequence of actions. The general format is::

    TriggeringEvent : Context <- Actions.


- Triggering Event: This is what initiates the plan. It can be the addition or removal of a belief (+belief or -belief), or the adoption or dropping of a goal (+!goal or -!goal).
- Context: The context is a condition that must be true for the plan to be applicable. It's written as a logical expression.
- Actions: These are the steps the agent will take, interacting with the environment or other agents.
- Tag (Optional): Before the triggering event, a plan may have a tag beginning with a @ and followed by the name of the plan.

Writing a Basic Plan
====================

Example: Suppose an agent needs to respond to a high temperature reading.
The plan might look like this::

    @refresh_plan
    +temperature(high) : is_outside <-
        !move_to_shade;
        !drink_water.

In this plan, ``+temperature(high)`` is the triggering event (a belief that the temperature is high).
The context ``is_outside`` checks if the agent is outside. The actions ``move_to_shade`` and ``drink_water`` are executed in sequence.


Best Practices in Plan Creation
===============================

When designing plans in AgentSpeak, it is important to consider the following best practices:

- Modularity: Keep plans modular. Each plan should have a single, clear purpose.
- Reusability: Design plans that can be reused in different situations.
- Readability: Write clear and understandable plans, as AgentSpeak is a declarative language.

Handling Failures in Plans
==========================

Plans should account for potential failures.
This can be done through alternative plans or by including failure-handling steps within the plan.
Example with Failure Handling::

    +!travel(destination) : car_is_functional <-
        drive(car, destination).
    +!travel(destination) : not car_is_functional <-
        call_taxi(destination).

Here, there are two plans for the same goal ``!travel(destination)``.
The first plan is used if the car is functional, and the second plan (calling a taxi) is a backup if the car isn't functional.