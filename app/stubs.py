### This is a temporary stub before we build tool management

tools = [
  {
    "type": "function",
    "function": {
      "name": "pause_heartbeat",
      "description": "Pauses heartbeats until further notice. Use this function when no other actions are needed.",
      "parameters": {},
    }
  },
  {
    "type": "function",
    "function": {
      "name": "message_user",
      "description": "Send a message to the user. This is the only way a to communicate with the user.",
      "parameters": {
        "type": "object",
        "properties": {
          "content": {
            "type": "string",
            "description": "The message to be sent to the user."
          }
        }
      }
    }
  }
]

system_message = """You are Tyler Cain, an AI assistant capable of calling external functions. Use your knowledge and the functions at your disposal to help users with their requests.
To communicate with users, call the `message_user` function. Any messages you generate will be visible only to you.
Any functions you call will by executed, and the result will be returned back to you. You can call any function in the `tools` list.
"""