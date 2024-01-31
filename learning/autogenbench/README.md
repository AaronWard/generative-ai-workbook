## AutogenBench

- [Blog Post](https://microsoft.github.io/autogen/blog)

Principles Summarized:

- **Repetition**: Because agent outputs can vary, autogen bench is design with allowing for repeating experiments in mind.

- **Isolation**: One agent may appear more efficient than the other simply because it ran second, and benefitted from the hard work the first agent did in installing and debugging necessary Python libraries. To address this, AutoGenBench isolates each task in its own Docker container. 

- **Instrumentation**: AutoGenBench is designed to log everything, and to compute metrics from those logs. To this end, AutoGenBench is designed to log everything, and to compute metrics from those logs. This ensures that one can always go back to the logs to answer questions about what happened, run profiling software, or feed the logs into tools like AgentEval.


## Install:

1. Install autogenbench
```bash
pip install autogenbench
```

2. Have docker installed

## Requirements:

1. An `OAI_CONFIG_LIST` file must be used.

```bash
export OAI_CONFIG_LIST=$(cat ./OAI_CONFIG_LIST)
```

## Setting up model:

Run ollama server locally
- `OLLAMA_HOST=127.0.0.1:5050 ollama serve`

```bash
curl http://localhost:5050/api/chat -d '{
   "model": "openhermes",
   "messages": [
     {
       "role": "user",
       "content": "why is the sky blue?"
     }
   ],
   "stream": false
}'
```


## Running an Evaluation:

For this example, we will run `HumanEval`

- `autogenbench clone HumanEval`



autogenbench run --subsample 0.1 --repeat 3 Tasks/human_eval_two_agents.jsonl


FIX:
```bash
(masterclass) LAMU0CLP74YXVX6:HumanEval award40$ autogenbench run --subsample 0.1 --repeat 3 Tasks/human_eval_two_agents.jsonl
Running scenario Results/human_eval_two_agents/HumanEval_107/0
Traceback (most recent call last):
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/connectionpool.py", line 715, in urlopen
    httplib_response = self._make_request(
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/connectionpool.py", line 416, in _make_request
    conn.request(method, url, **httplib_request_kw)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/connection.py", line 244, in request
    super(HTTPConnection, self).request(method, url, body=body, headers=headers)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 1283, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 1329, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 1278, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 1038, in _send_output
    self.send(msg)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 976, in send
    self.connect()
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/transport/unixconn.py", line 27, in connect
    sock.connect(self.unix_socket)
FileNotFoundError: [Errno 2] No such file or directory

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/requests/adapters.py", line 486, in send
    resp = conn.urlopen(
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/connectionpool.py", line 799, in urlopen
    retries = retries.increment(
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/util/retry.py", line 550, in increment
    raise six.reraise(type(error), error, _stacktrace)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/packages/six.py", line 769, in reraise
    raise value.with_traceback(tb)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/connectionpool.py", line 715, in urlopen
    httplib_response = self._make_request(
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/connectionpool.py", line 416, in _make_request
    conn.request(method, url, **httplib_request_kw)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/urllib3/connection.py", line 244, in request
    super(HTTPConnection, self).request(method, url, body=body, headers=headers)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 1283, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 1329, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 1278, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 1038, in _send_output
    self.send(msg)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/http/client.py", line 976, in send
    self.connect()
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/transport/unixconn.py", line 27, in connect
    sock.connect(self.unix_socket)
urllib3.exceptions.ProtocolError: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/api/client.py", line 214, in _retrieve_server_version
    return self.version(api_version=False)["ApiVersion"]
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/api/daemon.py", line 181, in version
    return self._result(self._get(url), json=True)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/utils/decorators.py", line 46, in inner
    return f(self, *args, **kwargs)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/api/client.py", line 237, in _get
    return self.get(url, **self._set_request_timeout(kwargs))
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/requests/sessions.py", line 602, in get
    return self.request("GET", url, **kwargs)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/requests/adapters.py", line 501, in send
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/award40/anaconda3/envs/masterclass/bin/autogenbench", line 8, in <module>
    sys.exit(main())
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/autogenbench/cli.py", line 83, in main
    command["function"]([invocation_cmd + " " + command["command"]] + args[2:])
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/autogenbench/run_cmd.py", line 605, in run_cli
    run_scenarios(
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/autogenbench/run_cmd.py", line 150, in run_scenarios
    run_scenario_in_docker(
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/autogenbench/run_cmd.py", line 355, in run_scenario_in_docker
    client = docker.from_env()
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/client.py", line 96, in from_env
    return cls(
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/client.py", line 45, in __init__
    self.api = APIClient(*args, **kwargs)
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/api/client.py", line 197, in __init__
    self._version = self._retrieve_server_version()
  File "/Users/award40/anaconda3/envs/masterclass/lib/python3.10/site-packages/docker/api/client.py", line 221, in _retrieve_server_version
    raise DockerException(
docker.errors.DockerException: Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))
(masterclass) LAMU0CLP74YXVX6:HumanEval award40$ 
```