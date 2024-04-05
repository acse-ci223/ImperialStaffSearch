import streamlit as st

__all__ = ["WebUI"]


class WebUI:
    def __init__(self):
        self.base()

    def base(self):
        st.set_page_config(page_title="Staff Finder", page_icon="🎓")
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        st.title("Staff Finder")
        project_search = st.text_input("Enter topics you're looking staff for: ")
        if st.button("Find Staff"):
            self.search(project_search)

    def search(self, project_search: str):
        st.write("Searching for staff...")
        if project_search:
            print(project_search)
        else:
            st.write("No topics entered. Please enter topics to search for staff.")