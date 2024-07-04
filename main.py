import os
import time
import pyautogui
from pynput import keyboard as pynput_keyboard
import threading
import openai
from openai import AsyncOpenAI
from io import BytesIO
import base64
import pygame
import asyncio
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class SlideDeck:
    def __init__(self):
        self.context = []
        self.narration_queue = asyncio.Queue()
        self.audio_queue = asyncio.Queue()
        self.is_playing = False
        self.lock = threading.Lock()

    async def capture_and_process_slide(self):
        # ...
        logging.info("Capturing and processing slide")
        screenshot = pyautogui.screenshot()
        base64_image = self.image_to_base64(screenshot)
        
        messages = self.context + [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "You are an AI assistant tasked with hosting a meetup. At the meetup, you will start the presentation and prepare the audience with the information from the slides. Don't describe the image. Extract the text from the image, and explain the text in a natural, engaging way as if you were presenting to an audience. Provide a concise narration suitable for text-to-speech conversion.Continue the presentation seamlessly from the previous slide, and explain it naturally as if presenting to an audience. Provide a concise narration that flows from the previous content. Keep the conversation in crisp, fun and engaging way"
                    }
                ]
            }
        ]
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",  # Changed from "gpt-4o" to "gpt-4-vision-preview"
                messages=messages,
                max_tokens=1000
            )
            
            narration = response.choices[0].message.content
            self.context.append({"role": "assistant", "content": narration})
            
            await self.narration_queue.put(narration)
            logging.info("Narration added to queue")
            logging.info(f"Queue size: {self.narration_queue.qsize()}")
        except Exception as e:
            logging.error(f"Error processing slide: {e}")

    async def generate_audio(self):
        while self.is_playing:
            if self.narration_queue.empty():
                await asyncio.sleep(0.1)
                continue

            narration = await self.narration_queue.get()
            logging.info("Narration retrieved from queue for audio generation")
            
            try:
                response = await client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=narration
                )

                # Get the audio content as bytes
                audio_content = response.read()
                
                # Add the audio content to the audio queue
                await self.audio_queue.put(audio_content)
                logging.info("Audio generated and added to audio queue")
            except Exception as e:
                logging.error(f"Error generating audio: {e}")

    async def stream_audio(self):
        self.is_playing = True
        pygame.mixer.init()
        logging.info("Audio streaming started")

        # Start the audio generation task
        audio_generation_task = asyncio.create_task(self.generate_audio())

        while self.is_playing:
            if self.audio_queue.empty():
                await asyncio.sleep(0.1)
                continue

            audio_content = await self.audio_queue.get()
            logging.info("Audio retrieved from audio queue")
            
            try:
                # Create a BytesIO object from the audio content
                audio_stream = BytesIO(audio_content)
                
                # Load and play the audio
                pygame.mixer.music.load(audio_stream)
                pygame.mixer.music.play()
                logging.info("Playing audio")

                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)

            except Exception as e:
                logging.error(f"Error playing audio: {e}")

        # Cancel the audio generation task when streaming stops
        audio_generation_task.cancel()

    async def transition_to_next_slide(self):
        logging.info("Transitioning to next slide")
        await self.capture_and_process_slide()
        
        if not self.is_playing:
            asyncio.create_task(self.stream_audio())

    def stop(self):
        self.is_playing = False
        pygame.mixer.music.stop()
        logging.info("Stopped audio playback")

    @staticmethod
    def image_to_base64(image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

slide_deck = SlideDeck()
event_queue = queue.Queue()

def on_press(key):
    try:
        if key.char == 'n':
            logging.info("Key 'n' pressed")
            event_queue.put('next')
        elif key.char == 'q':
            logging.info("Key 'q' pressed")
            event_queue.put('quit')
            return False
    except AttributeError:
        pass

async def handle_events():
    while True:
        try:
            event = event_queue.get_nowait()
            logging.info(f"Event '{event}' retrieved from queue")
            logging.info(f"Event queue size: {event_queue.qsize()}")
            if event == 'next':
                await slide_deck.transition_to_next_slide()
            elif event == 'quit':
                slide_deck.stop()
                return
        except queue.Empty:
            await asyncio.sleep(0.1)

async def main():
    logging.info("Press 'n' to capture and narrate the next slide. Press 'q' to quit.")
    
    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()

    await handle_events()

    listener.stop()

if __name__ == "__main__":
    asyncio.run(main())