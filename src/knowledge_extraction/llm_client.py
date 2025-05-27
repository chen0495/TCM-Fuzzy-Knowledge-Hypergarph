import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI, APIError

# Load environment variables from .env file
load_dotenv()

# TODO: Replace with actual import from common.config_loader if available
# from common.config_loader import load_config

# Placeholder function to load configuration. Keep until common.config_loader is implemented.
def load_config() -> Dict[str, Any]:
    """Loads configuration, prioritizing environment variables."""
    return {
        "llm": {
            "provider": "siliconflow",
            "api_key": os.environ.get("SILICONFLOW_API_KEY", "YOUR_API_KEY_HERE"),
            "model": os.environ.get("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3"),
            "api_url": os.environ.get("SILICONFLOW_API_URL", "https://api.siliconflow.cn/v1"),
            "default_max_tokens": 4096,
            "default_temperature": 0.1,
            "default_top_p": 0.7
        }
    }

class SiliconFlowClient:
    """Client for interacting with the SiliconFlow API using the OpenAI library."""

    def __init__(self):
        """Initializes the SiliconFlowClient."""
        config = load_config().get("llm", {})
        api_key = config.get("api_key")
        api_url = config.get("api_url") # Base URL for OpenAI client
        self.model_name = config.get("model")
        self.default_max_tokens = config.get("default_max_tokens", 4096)
        self.default_temperature = config.get("default_temperature", 0.1)
        self.default_top_p = config.get("default_top_p", 0.7)

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("SiliconFlow API key not configured. Set SILICONFLOW_API_KEY environment variable or update config.")
        if not api_url:
             raise ValueError("SiliconFlow API URL (base_url) not configured.")
        if not self.model_name:
             raise ValueError("SiliconFlow Model name not configured.")

        try:
            self.client = OpenAI(
                base_url=api_url,
                api_key=api_key
                # Consider adding timeout configuration if needed: http_client=httpx.Client(timeout=180.0)
            )
            print("OpenAI client for SiliconFlow initialized successfully.")
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            raise

    # No need for _prepare_headers or _prepare_payload with openai library

    def get_completion(self, prompt: str) -> Dict[str, Any]:
        """Gets a chat completion from the API using OpenAI library streaming,
           accumulates the content, and parses the final JSON.

        Args:
            prompt: The formatted prompt string.

        Returns:
            A dictionary parsed from the accumulated JSON response content.

        Raises:
            openai.APIError: If the API request fails.
            json.JSONDecodeError: If the accumulated content is not valid JSON.
            ValueError: If the stream finishes without accumulating content or other issues.
        """
        accumulated_content = ""
        content_str = None # Store final string for error reporting

        try:
            print("Initiating streaming request via OpenAI library...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=self.default_max_tokens,
                temperature=self.default_temperature,
                top_p=self.default_top_p,
                response_format={"type": "json_object"} # Request JSON format
            )
            print("Receiving stream...")

            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        accumulated_content += delta.content

            print("Stream processing complete. Parsing accumulated content...")
            if not accumulated_content:
                 raise ValueError("Stream finished, but no content was accumulated.")

            content_str = accumulated_content # Store for potential error reporting
            parsed_content = json.loads(accumulated_content)
            print("Successfully parsed accumulated JSON.")
            return parsed_content

        except APIError as e:
            print(f"SiliconFlow API error via OpenAI library: {e}")
            # Specific API error handling can be added here (e.g., retries for rate limits)
            raise
        except json.JSONDecodeError as e:
            print(f"Error decoding final accumulated JSON: {e}")
            print(f"Final accumulated string (may be truncated): '{content_str[:500]}...'") # Log problematic string
            raise
        except ValueError as e:
             print(f"Value error during stream processing: {e}")
             raise
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred during streaming: {e}")
            raise

# Removed the __main__ block for testing as it's not needed for integration.
# The script is intended to be imported and used via the SiliconFlowClient class. 