import os
from exa_py import Exa

# Fetch the API key from environment variables
api_key = os.getenv('EXA_API_KEY')

# Check if API key is provided
if api_key is None:
    raise ValueError("EXA_API_KEY environment variable is not set")

# Initialize the Exa object with the API key
exa = Exa(api_key)

# Now you can use the `exa` object to interact with the API


result = exa.search_and_contents(
  "hottest AI startups",
  type="neural",
  use_autoprompt=True,
  num_results=10,
  text=True,
)

print(result)