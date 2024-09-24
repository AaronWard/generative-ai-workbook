from duckduckgo_search import DDGS

# results = DDGS().text("Trump", max_results=5)
# for val in results:
#     print(val['title'])
#     print(val['href'])    
#     print(val['body'])
#     print()

results = DDGS().answers("Low-rank adaptor")
for val in results:
    print(val)    
    print()
