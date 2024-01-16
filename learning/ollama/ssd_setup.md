## How to move ollama models to SSD

I want to store local LLM models on an SSD, as keeping them on-machine takes up a lot of space. **Note**: You will probably want a USB-C compatible SSD with high transfer speeds. 

Here are some issues about the storage locations for ollama models:
- https://github.com/jmorganca/ollama/blob/main/docs/faq.md#where-are-models-stored
- https://github.com/jmorganca/ollama/issues/1625


Make a folder for ollama models:
> mkdir -p /Volumes/Extreme\ Pro/models/ollama/

Move models to SSD:
> mv ~/.ollama/models  /Volumes/Extreme\ Pro/models/ollama/

This will move the blob and manifest folders to your SSD

Create a symbolic link to new models location:
> ln -s /Volumes/Extreme\ Pro/models/ollama/models ~/.ollama/models

Test to see if models are visible
> ollama list

----

#### Misc:

Mounting the SSD: 

> sudo mkdir /Volumes/Extreme\ Pro
> diskutil list
> diskutil unmount /dev/disk5s1
> sudo mount_apfs /dev/disk5s1 /Volumes/Extreme\ Pro