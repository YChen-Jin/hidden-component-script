import base64
import os
import datetime
from zhipuai import ZhipuAI

# Image folder containing screenshots for analysis
img_folder = "images"


# List of questions for analyzing UI components
lines = [
    "Please carefully analyze the following app screenshot and identify any UI components that may be hidden or obscured.",
    "Hidden components are those that are not fully visible due to being covered by other UI elements, nested in complex layouts,",
    "or are part of scrollable areas. The components are not necessarily set to INVISIBLE or GONE, but might be obstructed or",
    "difficult to interact with in their current state.",
    "",
    "For each identified hidden component, provide the following details:",
    "1. **Component Type**: (e.g., Button, Spinner, TextView, ImageView, etc.)",
    "2. **Description**: A description of the component's position, size, and how it might be hidden or obscured (e.g., overlapping elements, scrolling behavior, or dynamic layout).",
    "3. **Hierarchy Information**: Provide insight into where the component is placed within the layout structure, and whether it's hidden by other elements or embedded within complex view hierarchies.",
    "4. **Interaction Path**: Suggest how a user might interact with the component or make it visible (e.g., by scrolling, expanding, or zooming).",
    "Additionally, include the extracted text from the screenshot, processed using OCR, to assist in the analysis:",
    # f"{'text_from_image'}"  #  replace 'text_from_image' with actual extracted text
]

question_list = []  # Questions list for inference


def buildPrompt():
    return "".join(line for line in lines)


def inference(img_path):
    stream_output = True
    history = []  # Ensure history is cleared before each inference
    images = []

    # Loop through files in the image folder and filter .jpg and .png files
    files = [os.path.join(img_path, f) for f in os.listdir(img_path) if
             os.path.isfile(os.path.join(img_path, f)) and (f.endswith(".jpg") or f.endswith(".png"))]
    for file in files:
        with open(file, 'rb') as img_file:
            images.append([base64.b64encode(img_file.read()).decode('utf-8'), file])

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"glm4v_{timestamp}.txt"
    file_path = os.path.join(img_path, file_name)

    # Write results to a file
    with open(file_path, 'a', encoding='utf-8') as file:
        for index, (img_base, img_name) in enumerate(images):
            result = do_inference(img_base, stream_output, history)
            file.write(f"Image: {img_name}\n")
            file.write("".join(result))
            if index < len(images) - 1:  # Add separator between images
                file.write("\n===============================================\n")


def do_inference(img_base, stream_output, history):
    result = []
    for question in question_list:
        print("User:", question)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_base
                        }
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]

        # Add history of previous interactions
        if history:
            for (q, a) in history:
                messages.append(
                    {
                        "role": "user",
                        "content": q
                    }
                )
                messages.append(
                    {
                        "role": "assistant",
                        "content": a
                    }
                )

        try:
            response = client.chat.completions.create(
                model="glm-4v-flash",
                messages=messages,
                stream=stream_output,
            )
            if stream_output:
                print("AI:", end="")
                final_text = ""
                for chunk in response:
                    current_text = chunk.choices[0].delta.content
                    final_text += current_text
                    print(current_text, end="")
                print("")
            else:
                final_text = response.choices[0].message.content
                print("AI:", final_text)

            # Append the conversation to the history
            history.append((question, final_text))
            result.append(final_text)

        except Exception as e:
            print(f"Error processing image: {e}")
            result.append(f"Error: {e}")

    return result


if __name__ == '__main__':

    # Ensure API Key is available
    api_key = "ea0d449c30fc2b9538a9441174e1afb8.qYg2g17CZxr8titI"
    if api_key == "None":
        print("Please provide your API key in the code.")
        exit(1)

    client = ZhipuAI(api_key=api_key)
    question_list.append(buildPrompt())

    # Iterate through files in the image folder and process each image
    file_name = os.listdir(img_folder)
    for file in file_name:
        img_path = os.path.join(img_folder, file)
        if os.path.isfile(img_path) and (file.endswith(".jpg") or file.endswith(".png")):
            inference(img_path)
