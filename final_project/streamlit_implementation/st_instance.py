import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli
import sys
from db_functions import *
from db_objects import *


# I will modify this in the near future.
# To use azure login for security. In the meantime, simple session states and passwords will do
def login():
    st.button("Already a User? Click This:")
    st.text_input()


def runner():
    login()


if __name__ == "__main__":
    if runtime.exists():
        st.set_page_config(page_title="Cooper Gradebook", page_icon="🎓")
        runner()
    else:
        sys.argv = [
            "streamlit",
            "run",
            "--client.showSidebarNavigation=False",
            sys.argv[0],
        ]
        sys.exit(stcli.main())
