
# DSPY




```bash
pip install dspy
pip install datasets
```



### Links:
- https://blog.isaacbmiller.com/posts/dspy
- https://substack.stephen.so/p/why-im-excited-about-dspy



---

## Deepseek V3

> I want an excuse to test out the Deepseek model, so what better way to do it than during testing out an agent framework.

Deepseek is a chinese LLM provider that has been getting a lot of hype lately. I've heard on many accounts that it performs better than the o1 model from OpenAI. Currently they only provide a single model, `deepseek-chat`, which is actually the DeepSeek-V3 model. It’s 3x faster than V2 (60 tokens/sec)

- https://www.deepseek.com/
- https://platform.deepseek.com/
- https://api-docs.deepseek.com/


DeepSeek uses a default temperature of 1.0. They provide recommended temperature settings for specific use cases:

| Use Case                 | Temperature |
|--------------------------|-------------|
| Coding / Math            | 0.0         |
| Data Cleaning / Analysis | 1.0         |
| General Conversation     | 1.3         |
| Translation              | 1.3         |
| Creative Writing/Poetry  | 1.5         |

They state that they have no rate limits, but it would be smart to implement retry logic in your code for 429 (Rate Limit Reached) or 503 (Server Overloaded).

DeepSeek can strictly enforce JSON output. This is helpful when you need structured data (e.g. for subsequent parsing). Set `response_format = {'type': 'json_object'}` in your request.

One of DeepSeek’s unique features is **Context Caching on Disk**:
- Automatic (no code changes needed).
- If two requests share a prefix, tokens in that prefix become “cache hits.”
- Cache hits are significantly cheaper than cache misses.