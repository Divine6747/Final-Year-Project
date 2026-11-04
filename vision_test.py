
from pathlib import Path
from ollama import chat


def analyse_screenshot(image_path):
    "Analyse a website screenshot using local vision AI."

    print("Sending screenshot to Qwen2.5-VL...")

    response = chat(
        model="qwen2.5vl:3b",
        messages=[
            {
                "role": "user",
                "content": """
                Analyse this Booking.com screenshot.

                Identify the following if visible:

                1. Destination search field
                2. Date selection controls
                3. Occupancy selector
                4. Cookie consent banner
                5. Pop-up windows
                6. Search button

                For each element, describe:
                - Its name
                - Its purpose
                - Its approximate screen position

                Only identify elements that are actually visible.
                """,
                "images": [str(image_path)]
            }
        ]
    )

    print("\n*** Vision AI Results ***\n")
    print(response.message.content)


if __name__ == "__main__":

    project_folder = Path(__file__).resolve().parent

    screenshot = project_folder / "booking_homepage.png"

    if screenshot.exists():
        analyse_screenshot(screenshot)
    else:
        print("Screenshot not found:", screenshot)
