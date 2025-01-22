import base64
import os
import datetime
import time

from zhipuai import ZhipuAI

img_folder = "images"
# 支持多轮对话

lines = [
    "Please analyze the following app screenshot and identify any UI components that may be hidden or obscured, even if they are not visible in the current state of the app. Focus on controls that could potentially appear based on specific user actions or conditions, but which are not visible in the screenshot itself.",
    "",
    "Hidden components often have the following characteristics and can be inferred even from a single screenshot:",
    "1. **Dynamically Loaded**: Controls that are not visible in the current screenshot but could appear after a specific user action such as a click, a swipe, or an animation. These controls are typically hidden when the app first loads.",
    # "2. **Conditionally Triggered**: Controls that might only become visible under certain conditions, such as after the user logs in, grants permissions, or selects certain options. Although not visible now, these controls can be inferred based on the app's design and the context of the screenshot.",
    "3. **UI State Changes**: Components that are likely to appear or change based on the app's state or user interactions. These could be triggered when transitioning between activities or when a menu is expanded.",
    "4. **Deep in the View Hierarchy**: Controls that are deeply nested in complex layouts and are not directly visible in the screenshot. These components might require special testing tools to identify, but they can still be inferred based on their typical locations or usage patterns.",
    # "5. **Transparency and Color**: Controls with low opacity or background-matching colors that are difficult to spot in the screenshot, but which are still part of the UI and may appear under certain conditions.",
    "6. **Interaction-Triggered Visibility**: Controls that could become visible or interactable after specific user inputs, such as tapping on a dropdown, pressing a button, or swiping on a screen. These controls might not be visible in the screenshot but are likely present and triggered based on the app's normal behavior.",
    "",
    "For each identified hidden component, provide the following details in JSON format:",
    "{",
    '"component_type": "Type of the component (e.g., Button, Spinner, TextView, ImageView, etc.)",',
    '"description": "Description of the component, including position, size, and how it might be hidden or obscured.",',
    '"hierarchy": "Details about the component’s position within the layout structure, and whether it’s obstructed or embedded within complex view hierarchies.",',
    '"interaction_path": "Suggested user interactions that might trigger the visibility of this component (e.g., tapping, scrolling, expanding, etc.)"',
    "}",
]



question_list = []

def buildPrompt():
    return "".join(line for line in lines)

def inference(img_path):
    stream_output = True
    history = []
    images = []

    files = [os.path.join(img_path, f) for f in os.listdir(img_path) if os.path.isfile(os.path.join(img_path, f)) and (f.endswith(".jpg") or f.endswith(".png"))]
    for file in files:
        with open(file, 'rb') as img_file:
            images.append([base64.b64encode(img_file.read()).decode('utf-8'), file])

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"glm_4v_flash_{timestamp}.txt"
    file_path = os.path.join(img_path, file_name)
    with open(file_path, 'a', encoding='utf-8') as file:
        for index, (img_base, img_name) in enumerate(images):
            result = do_inference(img_base, stream_output, history)
            file.write(f"Image: {img_name}\n")
            file.write("".join(result))
            if index < len(images) - 1:  # 如果不是最后一张图片，添加分隔线
                file.write("\n===============================================\n")
            time.sleep(3)  # 添加间隔5秒的代码，让每分析完一张图片后等待3秒再分析下一张

def do_inference(img_base, stream_output, history):
    result = []
    for question in question_list:
        print("User:", question)
        if history is None or len(history) == 0:
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
        else:
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
                            "text": history[0][0]
                        }
                    ]
                },
                {
                    "role": "assistant",
                    "content": history[0][1]
                }
            ]
            for (q, a) in history[1:]:
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
            messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

        response = client.chat.completions.create(
            # model="glm-4v-plus",
            model="glm-4v-flash",
            messages=messages,
            stream=stream_output,
            # temperature=0.1
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
        history.append((question, final_text)) # 将问题和回答添加到历史记录中

        result.append(final_text)

    return result

if __name__ == '__main__':
    api_key = "ea0d449c30fc2b9538a9441174e1afb8.qYg2g17CZxr8titI"  # 填写您自己的APIKey
    if api_key == "None":
        print("请在代码中填写您的APIKey")
        exit(1)
    client = ZhipuAI(api_key=api_key)
    question_list.append(buildPrompt())

    file_name = os.listdir(img_folder)
    for file in file_name:
        img_path = os.path.join(img_folder, file)
        inference(img_path)