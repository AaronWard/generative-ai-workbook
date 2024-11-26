ControlFlow is a Python framework for building AI workflows. It lets you create tasks for AI agents to handle - these agents can make decisions and do complex work on their own. You can combine tasks into flows to do bigger things.

### What ControlFlow Can Do:

- **Structured Results**: Get back organized data (using Pydantic), not just text
- **Custom Tools**: Use any Python function as a tool for agents
- **Team Up Agents**: Have multiple agents work together on tasks
- **Talk to Users**: Agents can ask for input and give feedback
- **Flows**: Chain tasks together with shared info and history

### Why Use ControlFlow:

- **Easy to Add**: Drops right into Python code
- **Stay in Control**: Keep tabs on what AI is doing
- **Grows With You**: Works for small scripts or big apps
- **See What's Up**: Watch how AI makes decisions
- **Quick Testing**: Try out AI features fast
- **Get More Done**: Focus on your code while ControlFlow handles the AI stuff


Links:
- [ControlFlow website](https://controlflow.ai/welcome)
- [Prefect Website](https://www.prefect.io/controlflow)
- [Github](https://github.com/PrefectHQ/controlflow)
- [Slack Channel](https://prefect.io/slack)

---

### `example1.ipynb`

- **What It Does**: This example demonstrates a basic email processing workflow using ControlFlow.
  - **Introduction to ControlFlow**: Introduces the basic usage of ControlFlow for managing workflows.
  - **Email Classification**: Creates an agent to classify emails as "important" or "spam" using a simple model.
  - **Agent Configuration**: Configures an agent with specific instructions and a model for classification.
  - **Processing Workflow**: Processes a list of emails and prints the classification results.

### `example2.ipynb`

- **What It Does**: This example shows how to create a workflow with dependent tasks that analyze text content.
  - **Dependent Tasks**: Demonstrates creating a workflow where tasks depend on each other for execution.
  - **Structured Results**: Uses Pydantic models to define structured data types for task results.
  - **Task Execution**: Executes a parent task that automatically runs dependent child tasks.
  - **Content Analysis**: Analyzes text to extract key information, generate summaries, and provide recommendations.
  - **Result Presentation**: Presents results in a structured format, including metadata and recommendations.

### `example3.ipynb`

- **What It Does**: This example implements a code review system using ControlFlow.
  - **Code Review System**: Demonstrates a system for reviewing code with structured feedback.
  - **Pydantic Models**: Defines a `CodeReview` model to structure the review results.
  - **Completion Tools**: Utilizes tools like `approve_code()` and `reject_code()` to handle review outcomes.
  - **Flow Function**: Implements a `review_code()` function to orchestrate the review process.
  - **Error Handling**: Includes error handling for task failures, such as validating if a number is even.

### `example4.ipynb`

- **What It Does**: This example explores creating and using agents with different perspectives and rules.
  - **Agent Creation**: Shows how to create simple and complex agents with different perspectives (e.g., optimist and pessimist).
  - **LLM Rules**: Demonstrates using default and custom LLM rules for agents.
  - **Task Execution**: Executes tasks with agents to analyze and summarize content.
  - **Custom Rules**: Defines custom rules for a hypothetical provider, showcasing flexibility in agent configuration.

### `example5.ipynb`

- **What It Does**: This example illustrates the use of flows to manage context and state in a trip planning scenario.
  - **Flow Management**: Introduces the concept of flows to maintain context and state across tasks.
  - **Trip Planning**: Demonstrates a flow for planning a trip, considering budget and duration constraints.
  - **Agent Collaboration**: Uses multiple agents (e.g., travel advisor, budget analyst) to optimize the trip plan.
  - **Budget Optimization**: Includes a sub-flow for optimizing the travel plan to fit within budget constraints.

### `example6.ipynb`

- **What It Does**: A simple example of using ControlFlow with Ollama.
  - **Task Definition**: Defines a task for the agent to write a snake game in Python.
