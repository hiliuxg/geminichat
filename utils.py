
import streamlit as st
import random, time
import google.generativeai as genai

"""https://ai.google.dev/api/rest/v1beta/HarmCategory?hl=zh-cn"""

SAFETY_SETTTINGS = [
    {
        "category": "HARM_CATEGORY_SEXUAL",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
]


class StateRender:

    def __init__(self, key):
        if key not in st.session_state:
            st.session_state[key] = []
    
    def get_state_by_key(self, key):
        return st.session_state[key]
    
    def add_state_item(self, key, role, content, to_load, prompt, load_tip):
        dic_item = {"role": role, "content": content, "to_load": to_load, "prompt": prompt, "load_tip": load_tip}
        st.session_state[key].append(dic_item)

    def render_state(self, key, call_fun):
        change_state = []
        for item in st.session_state[key]:
            if item["to_load"] and item['role'] == "assistant":
                with st.chat_message("assistant"):
                    finish_res = call_fun(item['prompt'], item["load_tip"])
                    dic_item = {"role": "assistant", "content": finish_res, "to_load": False, "prompt": "", "load_tip": ""}
            else:
                with st.chat_message(item["role"]):
                    st.markdown(item["content"])
                    dic_item = {"role": item["role"], "content": item["content"], "to_load": False, "prompt": "", "load_tip": ""}
            change_state.append(dic_item)
        st.session_state[key] = change_state
        


        