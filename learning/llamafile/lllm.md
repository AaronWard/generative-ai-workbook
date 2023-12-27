# `lllm.sh`

`lllm.sh` is a script for simplifying the running of Large Language Models (LLMs) using LlamaFile. It abstracts complex command-line operations into a more user-friendly format. This is inspired by IndyDevDan and his [setup](https://github.com/disler/lllm), but updated for my purposes. Add the command to with the following command:

```bash
source ./lllm.sh 
```

**Features**
- Supports multiple LLMs.
- Easy model execution via the command line.
- Options to run models as servers or with specific prompts.
- Capability to list all available models

**List Available Models:**
update the file to include new when you add a new llamafile model to your model folder.

```bash
./lllm.sh --list-models
```

**Run a Model with a Prompt:**

```bash
./lllm.sh "Write a story about llamas" mistral-main
```

**Run a Model as a Server on a Specific Port:**
```bash
./lllm.sh "" mistral-server 0.7 8081
```