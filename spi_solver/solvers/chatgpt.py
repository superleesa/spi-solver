import base64
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from openai import OpenAI


class OpenAIImageAnalyzer:
    PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "solve_spi_prompt.txt"
    SUPPORTED_MODELS = ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini"]

    def __init__(self, prompt: str | None = None, model_name: str = "gpt-4o") -> None:
        """
        Initialize the OpenAI client with the provided API key.

        Args:
            api_key (str): Your OpenAI API key.
        """
        load_dotenv()
        self.client = OpenAI()

        if prompt is None:
            with open(OpenAIImageAnalyzer.PROMPT_PATH, "r") as f:
                prompt = f.read()
        self.prompt = prompt

        if model_name not in OpenAIImageAnalyzer.SUPPORTED_MODELS:
            raise ValueError(
                f"Invalid model name. Supported models: {OpenAIImageAnalyzer.SUPPORTED_MODELS}"
            )
        self.model_name = model_name

    def _load_and_encode_image(self, image_path: str) -> str:
        """
        Load an image file and encode it as base64.

        Args:
            image_path (str): Path to the image file to load.

        Returns:
            str: Base64-encoded image data.
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            raise FileNotFoundError("Image file not found.")
        except Exception as e:
            raise Exception(f"Error reading the image file: {e}")

        return encoded_image

    def ask_about_picture(self, image_path: str) -> Generator[str, None, None]:
        """
        Sends a picture and a query to OpenAI's GPT-4 model with vision capabilities and streams the response.

        Args:
            image_path (str): Path to the image file to send.

        Yields:
            str: Chunks of the streaming response from the model.
        """
        encoded_image = self._load_and_encode_image(image_path)

        # see: https://platform.openai.com/docs/guides/vision#uploading-base64-encoded-images
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}",
                                    "detail": "low",  # TODO: experiment this: see https://platform.openai.com/docs/guides/vision#low-or-high-fidelity-image-understanding
                                },
                            },
                        ],
                    },
                ],
                stream=True,
            )

            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content

        except Exception as e:
            yield f"An error occurred while interacting with the OpenAI API: {e}"
