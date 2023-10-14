# chainlit-autogen

This is an example of using the chainlit chat interface with multi-agent conversation between agents to complete a tasks.

The tool has access to the path to a synthethic covid-19 dataset for example of how it can used by the agents for analysis. Context about this system level information such as paths are injected after the user submits a query.

> NOTE: I tried doing this on streamlit however it's basically impossible because streamlit is intended to be single threaded. There isn't a way to share messages if you were run the agents on a separate process (i tried) - Chainlit allows for asynchronousicity which allows you to run chainlit and autogen agents at the same time, therefore it is much cleaner to integrate with autogen.

**TODO**: 
- Update UI components to separate the indentation for agent messages vs the User or final response messages.
- Incorporate echart visualizations in the chainlit UI (is it possible?)

![img](ui.png)  
