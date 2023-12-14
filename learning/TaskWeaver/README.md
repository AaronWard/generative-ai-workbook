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
pip install -e . 
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

**Step 3: Update `taskweaver_config.json`**
Add this to the file, by leaving `llm.api_key` blank it will ask you in the terminal.
```json
{
    "llm.api_base": "https://api.openai.com/v1",
    "llm.api_key": "", // replace with your own
    "llm.model": "gpt-4-1106-preview"
}
```

**Step 4: Run Taskweaver**

You can run taskweaver in the CLI
```bash
python -m taskweaver -p ./<project name>
```

Or you can run as a library (see notebooks for examples)

----
