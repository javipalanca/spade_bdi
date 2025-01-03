===========================
Communication in AgentSpeak
===========================

Sending Messages
================

In AgentSpeak and multi-agent systems, communication is a key aspect of agent interaction.
This section covers the process and considerations for sending messages between agents in AgentSpeak, with a focus on the syntax, types of messages, and practical implementation.

Syntax for Sending Messages
---------------------------

AgentSpeak provides a simple and flexible syntax for sending messages. The general form includes specifying the type of communicative act (ilocution), the recipient agent, and the content of the message.

Basic Syntax::

    .send(recipient, ilocution, content)

where recipient is the identifier of the target agent, ilocution is the type of communicative act, and content is the message content.

Types of Communicative acts:
In AgentSpeak, communication between agents is achieved through illocutionary acts, often referred to as communicative acts.
Unlike performatives, which are more general in speech act theory, AgentSpeak uses specific types of illocutions to facilitate clear and purpose-driven agent interactions.
Here are the key illocutions used in AgentSpeak:

- ``tell``: Used to inform another agent about a belief. This act is about sharing knowledge or facts. For example, an agent might tell another agent that a specific condition is true::

    .send(agentB, tell, weather(raining));

- ``achieve``: Sent to request another agent to perform some action or bring about a certain state of affairs. This is similar to a request or command in conventional communication::

    .send(agentB, achieve, fix_the_leak);

- ``tellHow``: This illocution is used when an agent wants to inform another agent about how to perform a specific action or achieve a goal. It's about sharing procedural knowledge::

    .send(agentB, tellHow, "+!solve_problem <- !gather_data; !analyze_data.");

- ``askHow``: When an agent needs to know how to perform an action or achieve a goal, it uses askHow to request this procedural knowledge from another agent.::

    .send(agentB, askHow, learn_chess);

- ``untell``: This is used to inform another agent that a previously held belief is no longer true. It's a way of updating or correcting earlier information::

    .send(agentB, untell, weather(raining));

- ``unachieve``: Sent to request that another agent cease its efforts to achieve a previously requested goal. It's like a cancellation or retraction of a previous achieve request::

    .send(agentB, unachieve, fix_the_leak);

- ``untellHow``: Used to inform another agent to disregard previously told procedural knowledge. This might be used if the procedure is no longer valid or has been updated::

    .send(agentB, untellHow, "@plan_name");

Each of these illocutions plays a vital role in the communication protocol within a multi-agent system, allowing agents to share knowledge, coordinate actions, and update each other on changes in beliefs or plans. When designing AgentSpeak agents, it is crucial to implement these illocutions correctly to ensure effective and coherent agent interactions.

