import streamlit as st
from streamlit import runtime
from st_pages import hide_pages
from streamlit.web import cli as stcli
import sys
from time import sleep
from db_functions import *
from db_objects import *


# I will modify this in the near future.
# To use azure login for security. In the meantime, simple session states and passwords will do
def login_page():
    if not st.session_state["logged_in"]: 
        hide_pages(["login_page"])
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", key="password", type="password")
        login_button = st.button("Login",on_click=db_login,args=(username,password))
        if(login_button):
            st.write("Oops, seems like Your Credentials Are Wrong!")
            pass


        # if username == "test" and password == "test":
        #     st.session_state["logged_in"] = True
        #     hide_pages([])
        #     st.success("Logged in!")
        #     sleep(0.5)
        #     st.switch_page("pages/page1.py")

    else:
        st.write("Logged in!")
        st.button("log out", on_click=log_out)

def db_login(username,password):
    print(f"{username}, {password}")
    login_details = login(username,password)
    if(login_details[-1] > 0):
        st.session_state["logged_in"] = True
    # st.write("Logged In!")
    # sleep(3)
    pass

def log_out():
    st.session_state["logged_in"] = False
    st.success("Logged out!")
    sleep(0.5)


def runner():
    st.header("Welcome to the Gradebook! Please enter your username and Password.")
    login_page()


if __name__ == "__main__":
    if runtime.exists():
        st.set_page_config(page_title="Cooper Gradebook", page_icon="🎓")
        st.session_state["logged_in"] = False
        runner()
    else:
        sys.argv = [
            "streamlit",
            "run",
            "--client.showSidebarNavigation=False",
            sys.argv[0],
        ]
        sys.exit(stcli.main())
