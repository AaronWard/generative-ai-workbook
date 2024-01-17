## Local LLMs FAQ:

---

### What is Llama?

- [https://www.reddit.com/r/LocalLLaMA/wiki/index/](https://www.reddit.com/r/LocalLLaMA/wiki/index/)
- [https://en.wikipedia.org/wiki/LLaMA](https://en.wikipedia.org/wiki/LLaMA)
- [https://www.reddit.com/r/LocalLLaMA/comments/11o6o3f/how_to_install_llama_8bit_and_4bit/](https://www.reddit.com/r/LocalLLaMA/comments/11o6o3f/how_to_install_llama_8bit_and_4bit/)

### What is Lammacpp?

### What is GGML & GGUF?

- [https://deci.ai/blog/ggml-vs-gguf-comparing-formats-amp-top-5-methods-for-running-gguf-files/](https://deci.ai/blog/ggml-vs-gguf-comparing-formats-amp-top-5-methods-for-running-gguf-files/)

GGML, an earlier tensor library format, laid the groundwork but was limited by slower processing and lack of advanced features. GGUF, introduced in August 2023, is a significant improvement, offering a more efficient, flexible, user-friendly approach for storing and using LLMs. Key advantages of GGUF include single-file deployment, mmap compatibility, and support for quantization. It also adopts a key-value structure for metadata, enhancing extensibility and compatibility with older models. GGUF's design focuses on simplicity, efficiency, and addressing GGML's limitations, although transitioning existing models to GGUF can be time-consuming.


### What do the appendices mean?

### How to train LoRa?

- [https://github.com/oobabooga/text-generation-webui/wiki/05-%E2%80%90-Training-Tab](https://github.com/oobabooga/text-generation-webui/wiki/05-%E2%80%90-Training-Tab)

https://github.com/ggerganov/llama.cpp/pull/1684

### What is a TFLOP?

- A TFLOP (Tera Floating Point Operations Per Second) is a measure of a computer's performance, particularly in the context of graphics processing and scientific computations. It represents the ability to perform one trillion floating-point operations per second. In the context of graphics cards like Nvidia's models, FP16 (TFLOPS) and FP32 (TFLOPS) indicate the card's performance capability in executing 16-bit and 32-bit floating-point operations, respectively, at a rate of trillions per second. Higher TFLOP values generally signify greater computational power and efficiency in handling complex calculations, which is crucial for tasks like machine learning, 3D rendering, and high-performance computing.

### What is "Perplexity?"

A measure used in evaluating language models. It quantifies how well a probability model predicts a sample. A lower perplexity score typically indicates a better predictive performance of the model. In language modeling, perplexity assesses how well a model can predict or "understand" a sequence of text. For example, a language model with a lower perplexity would be more likely to accurately predict the next word in a sentence. The perplexity is calculated over a set number of chunks of text, using a specific batch size, to evaluate the model's performance.


### Cloud providers

- Vast.ai	
- Runpod
- Lambda Labs
- FluidStack
- Coreweave
- Paperspace
- Modal