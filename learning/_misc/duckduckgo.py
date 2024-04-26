from duckduckgo_search import DDGS

results = DDGS().text("python programming", max_results=5)
print(results)