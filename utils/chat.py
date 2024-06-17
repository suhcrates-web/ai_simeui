import streamlit as st


from service.modules import get_llm
from utils.path import load_edu_memory, save_edu_memory


def reset_memory():
    template = load_edu_memory('template')
    for i in range(0, 3):
        save_edu_memory(i, template)


def clear_session():
    try:
        st.cache_resource.clear()
        del st.session_state["current_page"]
        del st.session_state["messages"]
    except:
        pass


def init_chat():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        reset_memory()
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])


def enable_chat_history(func):
    # to clear chat history after swtching chatbot
    current_page = func.__qualname__
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = current_page
    if st.session_state["current_page"] != current_page:
        clear_session()
    
    init_chat()

    def execute(*args, **kwargs):
        func(*args, **kwargs)

    return execute


def display_msg(msg, author):
    """Method to display message on the UI

    Args:
        msg (str): message to display
        author (str): author of the message -user/assistant
    """
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)
