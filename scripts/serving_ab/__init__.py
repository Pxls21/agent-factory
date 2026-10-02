"""The A/B load harness for the PC's model server (task #454, D-127 to D-131; moved here from the session scratchpad by
task #462).

`make_workload.py` builds one fixed multi-chat workload and counts every prompt with the server's own `/tokenize` (chat
template included); `chat_load.py` replays it against an OpenAI-compatible server and records, per request, the time to
the first token, the decode rate, the token counts and the errors; `abwin.sh` is the GPU window job (D-088) that runs
the arms and brings vLLM back on every exit. Advisory: nothing here is a gate.
"""
