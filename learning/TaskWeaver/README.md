### TaskWeaver




- **Planner**: Manages task decomposition and execution.
- **Code Generator (CG)**: Generates Python code snippets from user requests, leveraging plugins and examples.
- **Code Executor (CE)**: Executes generated code and maintains execution context.

https://github.com/microsoft/TaskWeaver.git


### Setup

**Ste 1: Install**
```
git clone https://github.com/microsoft/TaskWeaver.git
cd TaskWeaver
pip install -r requirements.txt
```


**Step 2: Make folder structure**

Project folder should look like this:
```bash
📦project
 ┣ 📜taskweaver_config.json # the configuration file for TaskWeaver
 ┣ 📂plugins # the folder to store plugins
 ┣ 📂planner_examples # the folder to store planner examples
 ┣ 📂codeinterpreter_examples # the folder to store code interpreter examples
 ┣ 📂sample_data # the folder to store sample data used for evaluations
 ┣ 📂logs # the folder to store logs, will be generated after program starts
 ┗ 📂workspace # the directory stores session data， will be generated after program starts
    ┗ 📂 session_id 
      ┣ 📂ces # the folder used by the code execution service
      ┗ 📂cwd # the current working directory to run the generated code
```

Here is the command to do this quickly:
```bash
mkdir <some_project_name>
cd <some_project_name>
mkdir -p plugins planner_examples codeinterpreter_examples sample_data logs workspace/session_id/ces workspace/session_id/cwd
touch taskweaver_config.json

cd .. # cd outside the project directory
```

**Step 3: Update `taskweaver_config.json``
Add this to the file, by leaving `llm.api_key` blank it will ask you in the terminal.
```json
{
    "llm.api_base": "https://api.openai.com/v1",
    "llm.api_key": "", // replace with your own
    "llm.model": "gpt-4-1106-preview"
}
```

** Step 3: Run Taskweaver

You can run taskweaver in the CLI
```bash
python -m taskweaver -p ./<project name>
```

Or you can run as a library:
```
cd TaskWeaver
pip install -e . 
```




----



### Task Weaver vs Autogen:


**Task Weaver:**

- **Code Generation:** TaskWeaver’s primary advantage lies in its code-first design, which is especially beneficial for applications requiring direct manipulation and processing of data. It’s an effective tool for workloads that require interacting with code and data structures over abstract conversational models.
- Handling of complex data structures like pandas DataFrame.
- There are 3 components: Planner, Code Generator (CG), and Code Executor (CE). Autogen architecture is different, where the agent that corresponds with the human is the one who executes code. 
- TaskWeaver can be expanded into a multi-agent architecture for more complex projects and functionality.
 
**Autogen:**
- Human-AI Collaboration: Autogen allows for human interaction within a conversation
- Non data centric tasks: While TaskWeaver is ideal for data-centric tasks and analytics, AutoGen's capabilities extend to a broader range of dynamic, interactive applications. This makes AutoGen more versatile in handling diverse scenarios, from decision-making tasks to interactive games.