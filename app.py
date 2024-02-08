import streamlit as st
from streamlit_chat import message
from life_guru import LifeGuru
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
st.set_page_config(layout="wide")
st.session_state.clicked=True

@st.cache_resource(show_spinner=True)
def create_guruji():
    life_guru = LifeGuru()
    return life_guru
life_guru_ji = create_guruji()

def display_conversation(history):
    for i in range(len(history["apprentice"])):
        message(history["user"][i], is_user=True, key=str(i) + "_user")
        message(history["apprentice"][i], key=str(i))

if st.session_state.clicked:
    st.title("Life Guru")
    st.subheader("An AI Guru ji who can help you 24/7 by searching answers for your questions from vedas in realtime and provide you answers accordingly")

    if "apprentice" not in st.session_state:
        st.session_state["apprentice"] = ["What is your problem?"]
    if "user" not in st.session_state:
        st.session_state["user"] = ["Namaste!"]
    
    col1, col2 = st.columns([1,2])
    
    with col1:
        st.image("/home/harshsavasil/Workspace/life-guru/res/guruji.jpg")

    with col2:
        with st.expander("🙏"):
            research_query_input = st.text_input("Vatsa Sawal kya hai?")
            if st.button("Send"):
                robowiz_output = life_guru_ji.research(research_query_input)

                st.session_state["user"].append(research_query_input)
                st.session_state["apprentice"].append(robowiz_output)

                if st.session_state["apprentice"]:
                    display_conversation(st.session_state)