import io
import streamlit as st
import streamlit_scrollable_textbox as stx
import requests
import json

# Set the endpoint
ENDPOINT = "http://localhost:8000/profiles"
DEFAULT_IMAGE = "https://static.vecteezy.com/system/resources/previews/032/176/017/original/business-avatar-profile-black-icon-man-of-user-symbol-in-trendy-flat-style-isolated-on-male-profile-people-diverse-face-for-social-network-or-web-vector.jpg"

# Function to send POST request to the FastAPI server
def get_profiles(query):
    response = requests.post(ENDPOINT, json={"query": query})
    if response.status_code == 200:
        return response.json()['profiles']
    else:
        st.error("Failed to retrieve profiles")
        return []

# Streamlit app layout
st.title("Staff Finder")

# Search bar
query = st.text_input("Enter topics you're looking for:")

search_button = st.button("Search")

# Define a placeholder for search results right after the search bar
search_results_placeholder = st.empty()

# Function to display placeholders for profiles
def display_placeholders():
    with search_results_placeholder.container():
        for _ in range(3):
            # Adjust the width ratio as needed
            col1, col2 = st.columns([1, 5])
            
            with col1:
                st.image(DEFAULT_IMAGE, width=150, use_column_width=True)

            with col2:
                st.markdown("### Name")
                st.markdown("**Department:** Department")
                st.markdown("**Contact:** Contact")
                st.markdown("**Location:** Location")
                st.markdown("**Summary:** Summary")
                st.markdown("**Publications:**")
                st.text("Publication 1")
                st.text("Publication 2")
                st.markdown("[View Full Profile](https://www.example.com)", unsafe_allow_html=True)

            st.markdown("---")

# Function to display actual profiles
def display_profiles(profiles: list[dict]):
    search_results_placeholder.empty()
    
    with search_results_placeholder.container():
        for profile in profiles:
            col1, col2 = st.columns([1, 5])
            
            with col1:
                if 'url' in profile and profile['url']:
                    try:
                        img_data = requests.get(f"{profile['url']}/portrait.jpg").content
                        with io.BytesIO(img_data) as f:
                            f.seek(0)
                            st.image(f, width=150, use_column_width=True)
                    except Exception as e:
                        img_data = DEFAULT_IMAGE
                        st.image(img_data, width=150, use_column_width=True)

                    
                else:
                    st.image(DEFAULT_IMAGE, width=150, use_column_width=True)
            
            with col2:
                st.markdown(f"### {profile.get('name', 'N/A')}")
                st.markdown(f"**Department:** {profile.get('department', 'N/A')}")
                st.markdown(f"**Contact:** {profile.get('contact', 'N/A')}")
                st.markdown(f"**Location:** {profile.get('location', 'N/A')}")
                st.markdown(f"**Summary:**")
                stx.scrollableTextbox(profile.get('summary', 'N/A'), height=250, border=False)
                
                if profile.get('publications'):
                    st.markdown("**Publications:**")
                    stx.scrollableTextbox("\n".join(profile.get('publications', 'N/A')), height=250, border=False)
                else:
                    st.markdown("**Publications:** N/A")
                
                if 'url' in profile and profile['url']:
                    st.markdown(f"[View Full Profile]({profile['url']})", unsafe_allow_html=True)
                
            st.markdown("---")  # Horizontal line for separation

# Search button
if search_button:
    # Display placeholders initially
    display_placeholders()
    
    # Fetch and display actual profiles
    profiles = get_profiles(query)
    if profiles:
        display_profiles(profiles)
