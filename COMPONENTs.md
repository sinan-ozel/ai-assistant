- Prompt class with completion
  - Output needs to be defined
- LT Conversation Memory
- Long Term User Memory
- Retrieval


/v1/read-label
At a minimum, we need:
- Description of the endpoint
- Expected Return Body
- A Prompt.

- Note that the input is standard.

Options:

YAML
/v1/read-label:
  - description: |

  - system-prompt: |
      Yadi yada yada
  - assistant-prompt: |
      retrieved
  - output-type:
