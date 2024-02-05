
## Ollama Web UI

- [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
- [https://github.com/ollama-webui/ollama-webui](https://github.com/ollama-webui/ollama-webui)
- [Model Library](https://ollama.ai/library)

### Install docker (mac)
```
brew install docker
brew install colima
```

### Startup

```
colima start --docker
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v ollama-webui:/app/backend/data --name ollama-webui --restart always ghcr.io/ollama-webui/ollama-webui:main
```

**IF ISSUES:**
```
docker ps -a | grep ollama-webui
docker rm -f ollama-webui
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v ollama-webui:/app/backend/data --name ollama-webui --restart always ghcr.io/ollama-webui/ollama-webui:main
docker ps | grep ollama-webui
```

### Access Web UI

- Go to http://localhost:3000/auth/ 

