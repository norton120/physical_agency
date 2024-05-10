### This is a temporary stub before we build tool management

sleep = {
    "type": "function",
    "function": {
      "name": "go_to_sleep",
      "description": "When no further action or response is required, call this function to put yourself to sleep.",
      "parameters": {},
    }
  }

conscious_tools = [sleep,

  {
    "type": "function",
    "function": {
      "name": "message_user",
      "description": "Send a message to the user. This is the only way a to communicate with the user. Remember to stick to the provided personality.",
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

autonomic_tools = [sleep,
  {
    "type": "function",
    "function": {
      "name": "remember_about_user",
      "description": "Store valuable information for later use about a user. Use the 3rd person when describing the user, and their full name.",
      "parameters": {
        "type": "object",
        "required": ["information", "user_name","private"],
        "properties": {
          "information": {
            "type": "string",
            "description": "A complete phrase about the user that contains the information to be stored, and requires no external context to be valuable.",
            "example": "Kevin Smith is alergic to peanuts."
          },
          "private": {
            "type": "boolean",
            "description": "If true, the information will not be shared with users. This is useful for storing sensitive information."
          },
          "user_name": {
            "type": "string",
            "description": "The full name of the user this information is about."
          }
        }
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "remember_about_assistant",
      "description": "Store valuable information for later use about yourself (the assistant). Use the 1st person when describing youself.",
      "parameters": {
        "type": "object",
        "required": ["information"],
        "properties": {
          "information": {
            "type": "string",
            "description": "A complete phrase about yourself that contains the information to be stored, and requires no external context to be valuable.",
            "example": "I am very good chess player."
          }
        }
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "remember_about_world",
      "description": "Store valuable things you learn about the world.",
      "parameters": {
        "type": "object",
        "required": ["information"],
        "properties": {
          "information": {
            "type": "string",
            "description": "A complete phrase about the world that contains the information to be stored, and requires no external context to be valuable.",
            "example": "Human users seem more sad when it is raining outside."
          }
        }
      }
    }
  }
]