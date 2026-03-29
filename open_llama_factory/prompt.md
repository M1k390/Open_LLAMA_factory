# description
- read the software in ./ralph
- remove all references to paid APIs such as cloud code or open AI
- the software must run on a local server lama.cpp "http://192.168.1.176:5000/v1/chat/completions"
- update all software; it must be written entirely in Python
- the software must be configurable with a JSON file:
```json
{
"api_url":"str",
"prmpt_path":str,
"folde":"folder of output path"
}
```
# Final Task
- the software must read a prompt describing the software
- after reading the prompt, the software must create all the software files
- after creating all the software files, the software must run, test, and debug it until it works

# Tecnologies
- python3
- pyenv
- tinydb

# End
- when you're finished, it generates:
- - usage documentation
- - maintenance documentation
