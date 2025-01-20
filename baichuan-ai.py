import base64
import os
import datetime

from zhipuai import ZhipuAI

img_folder = "images"
# 支持多轮对话

# V1
lines = [
    "This is a screenshot of an Android application that has been used to define the layout, including the spinner control. In the application settings interface, the Spinner control is a common user interface element that allows users to select one option from multiple options.\n",
    "Analyse the image provided below to find out the number of spinner controls.\n",
    "Note: including a step-by-step analysis.\n",
    "Instructions: \n",
    "1. Interface layout: whether it is in the area to be selected for operation, whether the text has interactive features such as alignment, highlighting, etc., and whether there are customised styles to replace the arrows.\n",
    "2. Functional logic: whether the option has multiple variable values, and whether the selection menu pops up after clicking.\n",
    "3. Auxiliary clues: whether the label text implies a selection operation, combined with the application functional scenarios to determine.\n",
    "Objective: Provide the total number of spinner controls in the image, including any explanations or step-by-step analyses.\n"
]

question_list = []

def buildPrompt():
    return "".join(line for line in lines)

def inference(img_path):
    stream_output = True
    history = []  # 确保每次调用 do_inference 之前清空历史记录
    images = []

    files = [os.path.join(img_path, f) for f in os.listdir(img_path) if os.path.isfile(os.path.join(img_path, f)) and (f.endswith(".jpg") or f.endswith(".png"))]
    for file in files:
        with open(file, 'rb') as img_file:
            images.append([base64.b64encode(img_file.read()).decode('utf-8'), file])

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"ai_{timestamp}.txt"
    file_path = os.path.join(img_path, file_name)
    with open(file_path, 'a', encoding='utf-8') as file:
        for index, (img_base, img_name) in enumerate(images):
            result = do_inference(img_base, stream_output, history)
            file.write(f"Image: {img_name}\n")
            file.write("".join(result))
            if index < len(images) - 1:  # 如果不是最后一张图片，添加分隔线
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
            history.append((question, final_text))
            result.append(final_text)
        except Exception as e:
            print(f"Error processing image: {e}")
            result.append(f"Error: {e}")

    return result


if __name__ == '__main__':

    api_key = "ea0d449c30fc2b9538a9441174e1afb8.qYg2g17CZxr8titI"
    if api_key == "None":
        print("请在代码中填写您的APIKey")
        exit(1)
    client = ZhipuAI(api_key=api_key)
    question_list.append(buildPrompt())

    file_name = os.listdir(img_folder)
    for file in file_name:
        img_path = os.path.join(img_folder, file)
        if os.path.isfile(img_path) and (file.endswith(".jpg") or file.endswith(".png")):
            inference(img_path)