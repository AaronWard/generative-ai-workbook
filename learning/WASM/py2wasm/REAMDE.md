

- [Article](https://wasmer.io/posts/py2wasm-a-python-to-wasm-compiler)
- [Docs](https://pypi.org/project/py2wasm/#usage)
- [Video](https://www.youtube.com/watch?v=_Gq273qvNMg)
- [WAGI](https://www.fermyon.com/blog/python-wagi)

### Setup:

1. `conda create --name wasm python==3.11`
2. `pip install py2wasm`
3. `py2wasm main.py -o main.wasm`


This will take a while to build...


4. `brew install wasmer` - to run compiled WASM
5. `wasmer run main.wasm`