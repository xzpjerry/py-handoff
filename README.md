# py-handoff: Like Handoff, but in Python

## Usage
On each Windows/MacOS/Linux devices connected to the same LAN, run the following command:
```
    pip install py-handoff
    py-handoff
```
Now all you devices would share their clipboard.

## Optional Config
### Port
By exporting "PY_HANDOFF_PORT=<port_number:int>", you can customize the port py-handoff used for communication.
### Secret Key
Similarly, exporting "PY_HANDOFF_KEY=<secret_key:str>", you can customize the secret key py-handoff used to obfuscate its connections.

Keep in mind that all py-handoff instances can only reconize and communicate with each other if and only if they have the same port number and the same secret key.