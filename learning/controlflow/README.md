ControlFlow is a Python framework designed for building agentic AI workflows. It allows developers to create workflows that delegate tasks to LLM (Large Language Model) agents, which are autonomous entities capable of making decisions and performing complex tasks. The framework emphasizes a task-centric approach, enabling the creation of discrete, observable tasks that can be assigned to specialized AI agents. These tasks can be combined into flows to orchestrate more complex behaviors.

### Key Features of ControlFlow:

- **Structured Results**: Tasks can return structured data types supported by Pydantic, not just text.
- **Custom Tools**: Developers can provide any Python function as a tool for agents to use.
- **Multi-agent Collaboration**: Multiple agents can be assigned to a task to enable collaboration.
- **User Interaction**: Agents can interact with users, allowing for dynamic input and feedback.
- **Flows**: Complex workflows can be created by running tasks with a shared context and message history.

### Benefits of Using ControlFlow:

- **Seamless Integration**: Easily integrate AI capabilities with existing Python codebases.
- **Fine-grained Control**: Maintain oversight and control over AI workflows.
- **Scalability**: Suitable for both simple scripts and complex applications.
- **Transparency**: Provides insights into AI decision-making processes.
- **Rapid Prototyping**: Facilitates quick experimentation with AI-powered features.
- **Productivity**: Focus on application logic while ControlFlow manages AI orchestration.

For more detailed information, you can visit the [ControlFlow website](https://controlflow.ai/welcome).


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
