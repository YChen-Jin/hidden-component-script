import base64
import os
import datetime
import time

from zhipuai import ZhipuAI

img_folder = "images"
# 支持多轮对话

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