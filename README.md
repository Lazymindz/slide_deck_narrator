# SlideDeck Narrator

SlideDeck Narrator is an automation tool that captures and narrates slides during a presentation using OpenAI's API for text generation and text-to-speech capabilities.

## Features

- Captures the current slide as a screenshot.
- Extracts and narrates the content of the slide using OpenAI's GPT-4-vision-preview model.
- Streams the narration audio in real-time using Pygame.
- Listens for keyboard inputs to control slide transitions and application termination.

## Requirements

- Python 3.7+
- OpenAI API Key
- Required Python packages:
  - `pyautogui`
  - `pynput`
  - `pygame`
  - `openai`
  - `asyncio`
  - `queue`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/SlideDeckNarrator.git
    cd SlideDeckNarrator
    ```

2. Install the required packages:
    ```bash
    pip install pyautogui pynput pygame openai asyncio
    ```

3. Set up your OpenAI API key:
    ```bash
    export OPENAI_API_KEY='your-openai-api-key'
    ```

## Usage

1. Run the main script:
    ```bash
    python main.py
    ```

2. During the presentation, use the following keyboard controls:
    - Press 'n' to capture and narrate the next slide.
    - Press 'q' to quit the application.

## Code Overview

### SlideDeck Class

- **`__init__`**: Initializes the context, narration queue, and playback state.
- **`capture_and_process_slide`**: Captures a screenshot, processes it with OpenAI, and queues the narration.
- **`stream_audio`**: Streams and plays narration audio from the queue.
- **`transition_to_next_slide`**: Captures and processes the next slide.
- **`stop`**: Stops the audio playback.
- **`image_to_base64`**: Converts an image to a base64 encoded string.

### Event Handling

- **`on_press`**: Listens for specific key presses ('n' for next slide, 'q' for quit).
- **`handle_events`**: Processes keyboard events to control slide transitions and application termination.

### Main Script

- Initializes the SlideDeck instance.
- Sets up the keyboard listener.
- Handles events in an asynchronous loop.

## To Do
- [ ] Streaming audio

## Contributing

Feel free to fork and make changes.

## License

This project is licensed under the MIT License.
