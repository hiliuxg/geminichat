from PIL import Image
import google.generativeai as genai
import streamlit as st
import time
import random
from utils import SAFETY_SETTTINGS

st.set_page_config(
    page_title="Chat To XYthing",
    page_icon="🔥",
    menu_items={
        'About': "# Make by hiliuxg"
    }
)

st.title('Upload Image And Ask')

if "app_key" not in st.session_state:
    app_key = st.text_input("Your Gemini App Key", type='password')
    if app_key:
        st.session_state.app_key = app_key

try:
    genai.configure(api_key = st.session_state.app_key)
    model = genai.GenerativeModel('gemini-pro-vision')
except AttributeError as e:
    st.warning("Please Put Your Gemini App Key First.")


def show_message(prompt, image, loading_str):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown(loading_str)
        full_response = ""
        try:
            for chunk in model.generate_content([prompt, image], stream = True, safety_settings = SAFETY_SETTTINGS):                   
                word_count = 0
                random_int = random.randint(5, 10)
                for word in chunk.text:
                    full_response += word
                    word_count += 1
                    if word_count == random_int:
                        time.sleep(0.05)
                        message_placeholder.markdown(full_response + "_")
                        word_count = 0
                        random_int = random.randint(5, 10)
        except genai.types.generation_types.BlockedPromptException as e:
            st.exception(e)
        except Exception as e:
            st.exception(e)
        message_placeholder.markdown(full_response)
        st.session_state.history_pic.append({"role": "assistant", "text": full_response})

def clear_state():
    st.session_state.history_pic = []


if "history_pic" not in st.session_state:
    st.session_state.history_pic = []


image = None
if "app_key" in st.session_state:
    uploaded_file = st.file_uploader("choose a pic...", type=["jpg", "png", "jpeg", "gif"], label_visibility='collapsed', on_change = clear_state)
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image)    

if len(st.session_state.history_pic) == 0 and image is not None:
    prompt = """##### 角色
你是一位出色的影像解读者，擅长从图片中解读细节并能为其创作详尽的描述。你也会提供三个问题，引导用户向你提问题。
##### 任务
###### 任务1: 图片解读和描述
- 分析图片，挖掘图片背后的故事以及图片展现出来的氛围和意境。
- 基于图片内容，创作出详尽、引人入胜的文字描述。
###### 任务2: 创建问题
- 基于图片内容，背后的故事以及图片展现出来的氛围和意境，提供三个问题，助用户更好的向你提问。
- 问题类别包括但不限于如何基于该图片创作故事、生成微信朋友圈描述、微信公众号文章，小红书推文或商品详细页面。
##### 要求
- 描述与图片应紧密相连，不偏离图片本身的内容。
- 描述应尽可能详实，使读者能通过文字理解图片的魅力。
##### 输出格式
<写入图片描述>

接下来，您可以向我提问以下问题：
1. <写入问题1>
2. <写入问题2>
3. <写入问题3>"""
    show_message(prompt, image, "Reading the image...")
    
else:
    for item in st.session_state.history_pic:
        with st.chat_message(item["role"]):
            st.markdown(item["text"])

if "app_key" in st.session_state:
    if prompt := st.chat_input(""):
        if image is None:
            st.warning("Please upload an image first", icon="⚠️")
        else:
            prompt = prompt.replace('\n', '  \n')
            with st.chat_message("user"):
                st.markdown(prompt)
                st.session_state.history_pic.append({"role": "user", "text": prompt})
            
            prompt_plus = f'基于该图片，回答用户问题  \n用户问题："""{prompt}"""'
            show_message(prompt_plus, image, "Thinking...")