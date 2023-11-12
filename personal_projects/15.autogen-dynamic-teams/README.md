# Autogen Dynamic Teams

The goal here is build a respository of system messages, which define a role in which an agent is supposed to act out. Essentially, the


1. **Complexity Assessment:** The initial LLM evaluates the complexity of the user's query.

2. **Dynamic Team Formation:** Teams are formed based on the task's complexity, available resources, and agent roles. Simpler tasks use fewer agents, and complex tasks may require a multi-agent setup.

3. **Agent Delegation:** The task is delegated to the selected agents, who either w3.ork together or independently to resolve the task.

4. **Efficiency and Cost-Effectiveness:** The system prefers two-way interactions over group chats for simple tasks to optimize costs.