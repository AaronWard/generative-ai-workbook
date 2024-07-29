
## Ollama Web UI

- [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
- [https://github.com/ollama-webui/ollama-webui](https://github.com/ollama-webui/ollama-webui)
- [Model Library](https://ollama.ai/library)

- [New Github Repo Link](https://github.com/open-webui/open-webui?tab=readme-ov-file)
- [Setup Docs](https://docs.openwebui.com/getting-started/)

### Install docker (mac)
```
brew install docker
brew install colima
```

### Startup

```
colima start --docker
```

---

#### Before namechange and update (legacy)


```
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v ollama-webui:/app/backend/data --name ollama-webui --restart always ghcr.io/ollama-webui/ollama-webui:main
```


**IF ISSUES:**
```
docker ps -a | grep ollama-webui
docker rm -f ollama-webui
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v ollama-webui:/app/backend/data --name ollama-webui --restart always ghcr.io/ollama-webui/ollama-webui:main
docker ps | grep ollama-webui
```


#### After namechange and update

> Ollama webui changed their name 


```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

There is now python tool to handle spinning up the server:

```bash
conda create -n open-webui python=3.11
conda activate open-webui
pip install open-webui
open-webui serve
```


---

### Access Web UI

- Go to http://localhost:3000/auth/ 



---


### Enabling search

- https://docs.openwebui.com/tutorial/web_search#searxng-docker

If you get:

```bash
HTTPConnectionPool(host='searxng', port=8080): Max retries exceeded with url: /search?q=Search+latest+news+about+disney&format=json&pageno=1&safesearch=1&language=en-US&time_range=&categories=&theme=simple&image_proxy=0 (Caused by NameResolutionError("<urllib3.connection.HTTPConnection object at 0x329e7ea10>: Failed to resolve 'searxng' ([Errno 8] nodename nor servname provided, or not known)"))
```

Use this to get the local ip address of the running container:
```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' searxng
```


