
## MeloTTS

Note: this is for Macbook only. Clone the repo and `cd` into the repository.

### Python env install:


```bash
pip3 download mecab-python3
ls
brew install mecab
brew reinstall mecab
/opt/homebrew/bin/brew install mecab --build-from-source
brew uninstall mecab
/opt/homebrew/bin/brew install mecab --build-from-source
pip install unidic-lite
ARCHFLAGS='-arch arm64' pip install --compile --use-pep517 --no-cache-dir --force mecab-python3==1.0.5


pip install -e .
python -m unidic download

```

### Docker install

> this didn't work for me.

```
colima start
docker build -t melotts . 
```

```
docker run -it -p 8888:8888 melotts
```