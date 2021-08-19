# py-handoff: Like Handoff, but in Python
py-handoff is an application used to share clipboard contents across your devices connected to the same LAN.

## Usage
On each Windows/macOS/Linux device connected to the same LAN, run the following command:
```
    pip install py-handoff
    py-handoff
```
Now all your devices would share their clipboard.

## Optional Environment Variables
### PY_HANDOFF_DISCOVERY_PORT
By setting "PY_HANDOFF_DISCOVERY_PORT=<port_number: int>", you can customize the port that py-handoff used to discover other py-handoff applications in the same LAN through UDP; defaults to 5005.
### PY_HANDOFF_DISCOVERY_KEY
By setting "PY_HANDOFF_DISCOVERY_KEY=<secret_key:str>", you can customize the secret key py-handoff used to encode/decode messages during the discovery phase; defaults to "D0AA67DD-C285-45A2-B7A7-F5277F613E3C".
### PY_HANDOFF_CLIPBOARD_LISTENER_PORT
By setting "PY_HANDOFF_CLIPBOARD_LISTENER_PORT=<port_number: int>", you can customize the port that py-handoff used to accept clipboard contents sent by other py-handoff applications in the same LAN through TCP; defaults to 6000.
### PY_HANDOFF_CLIPBOARD_SIZE_LIMIT_IN_MB
By setting "PY_HANDOFF_CLIPBOARD_SIZE_LIMIT_IN_MB=<size: int>", you can customize the maximum size of clipboard contents in MB that py-handoff would send to other py-handoff applications that have been discovered; defaults to 128 MB.

Keep in mind that all py-handoff applications can only recognize and communicate with each other if and only if they have **the same PY_HANDOFF_DISCOVERY_PORT** and **the same PY_HANDOFF_DISCOVERY_KEY**.