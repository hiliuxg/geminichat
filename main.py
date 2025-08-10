
from numpy import full
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Chat To XYthing",
    page_icon="🔥",
    menu_items={
        'About': "# Make By hiliuxg"
    }
)

st.title("Chat To XYthing")
st.caption("a chatbot, powered by multiple LLMs.")

# 读取配置文件
import toml
config = toml.load(".streamlit/secrets.toml")

# 添加秘钥验证状态
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 秘钥验证界面
if not st.session_state.authenticated:
    st.markdown("### 🔐 请输入秘钥以继续")
    secret_key = st.text_input("秘钥", type="password", placeholder="请输入秘钥...")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("验证", type="primary", use_container_width=True):
            if secret_key == config.get("access", {}).get("access_key", ""):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 秘钥错误，请重试")
    
    st.stop()

# 以下是原有的聊天界面代码，只有在验证通过后才会执行
models_config = config.get("models", {})

# Initialize session state variables
if "app_key" not in st.session_state:
    st.session_state.app_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = ""
if "base_url" not in st.session_state:
    st.session_state.base_url = ""
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = ""

if "history" not in st.session_state:
    st.session_state.history = []
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "top_p" not in st.session_state:
    st.session_state.top_p = 1.0

# Model selection in sidebar
with st.sidebar:
    st.subheader("Model Selection")
    model_names = list(models_config.keys())
    selected_model = st.selectbox("Choose a model", model_names, index=0)
    
    # Update session state with selected model's configuration
    if selected_model in models_config:
        api_key, base_url, model_name = models_config[selected_model]
        st.session_state.app_key = api_key
        st.session_state.base_url = base_url
        st.session_state.model_name = model_name
    
    st.divider()
    
    # Model parameters
    st.subheader("Model Settting")
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="控制输出的随机性，值越高输出越随机"
    )
    st.session_state.temperature = temperature
    
    top_p = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.top_p,
        step=0.1,
        help="控制输出token的累积概率阈值"
    )
    st.session_state.top_p = top_p
    
    # System prompt
    system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state.system_prompt,
        height=300,
        help="设置AI助手的系统提示词，用于定义AI的行为和角色"
    )
    st.session_state.system_prompt = system_prompt
    
    # Clear chat history button
    if st.button("Clear Chat Window", key="clear_chat_1", use_container_width = True, type="primary"):
        st.session_state.history = []
        st.rerun()

# Set OpenAI configuration
try:
    client = OpenAI(api_key=st.session_state.app_key, base_url=st.session_state.base_url)
except AttributeError as e:
    st.warning("Please select a model and provide the API key.")

# For DeepSeek, we'll use the chat.completions API
# We'll manage history manually since there's no direct equivalent to start_chat

# Display chat history
for message in st.session_state.history:
    role = "assistant" if message["role"] == "assistant" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# Since DeepSeek API doesn't have a direct equivalent to start_chat,
# we'll manage the conversation history manually.

if "app_key" in st.session_state:
    if prompt := st.chat_input(""):
        prompt = prompt.replace('\n', '  \n')
        # Add user message to history
        st.session_state.history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                full_response = ""
                # 构建包含system prompt的消息列表
                messages = []
                if st.session_state.system_prompt:
                    messages.append({"role": "system", "content": st.session_state.system_prompt})
                messages.extend(st.session_state.history)
                
                # Use OpenAI's chat.completions API with the selected model
                response = client.chat.completions.create(
                    model=st.session_state.model_name,
                    messages=messages,
                    stream=True,
                    temperature=st.session_state.temperature,
                    top_p=st.session_state.top_p,
                )

                start_thing = False
                has_start = False
                for chunk in response:
                    reasoning_content = chunk.choices[0].delta.reasoning_content
                    if reasoning_content:
                        if not start_thing:
                            full_response += ">"
                            start_thing = True

                        if has_start:
                             full_response += ">"
                             has_start = False

                        if reasoning_content.startswith("  \n") or reasoning_content.startswith("\n"):
                            has_start = True

                        if reasoning_content.endswith("  \n") or reasoning_content.endswith("\n"):
                            has_start = True    

                        full_response += reasoning_content

                    ## 开始正文
                    content = chunk.choices[0].delta.content
                    if content:
                        if start_thing:
                            full_response += "  \n  \n"
                            start_thing = False
                        full_response += content
                    
                    message_placeholder.markdown(full_response + "_")

                message_placeholder.markdown(full_response)
                
                # Add assistant response to history
                st.session_state.history.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.exception(e)