import io
import streamlit as st
import streamlit_scrollable_textbox as stx
import requests
import json

# Set the endpoint
ENDPOINT = "http://backend:8000/profiles"
DEFAULT_IMAGE = "https://static.vecteezy.com/system/resources/previews/032/176/017/original/business-avatar-profile-black-icon-man-of-user-symbol-in-trendy-flat-style-isolated-on-male-profile-people-diverse-face-for-social-network-or-web-vector.jpg"

# Function to send POST request to the FastAPI server
def get_profiles(query) -> list[dict] | None:
    """Send a POST request to the FastAPI server to retrieve profiles based on the query.
    
    Parameters
    ----------
    query : str
        The query to search for.
        
    Returns
    -------
    list[dict] | None
        A list of profiles if the request is successful, otherwise None.
    """
    try:
        response = requests.post(ENDPOINT, json={"query": query})
        if response.status_code == 200:
            return response.json()['profiles']
        else:
            st.error("Failed to retrieve profiles")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

st.set_page_config(page_title="Staff Finder", page_icon="🎓")

# Streamlit app layout
st.title("🎓Imperial College Staff Finder")

# Search bar
query = st.text_input("Enter topics you're looking for:")

search_button = st.button("Search")

# Define a placeholder for search results right after the search bar
search_results_placeholder = st.empty()

# Function to display placeholders for profiles
def display_placeholders():
    """Display placeholders for profiles while the actual profiles are being fetched."""
    with search_results_placeholder.container():
        for id in range(3):
            # Adjust the width ratio as needed
            col1, col2 = st.columns([1, 5])
            
            with col1:
                st.image(DEFAULT_IMAGE, width=150, use_column_width=True)

            with col2:
                st.markdown("### Loading...")
                st.markdown("**Department:** Loading...")
                st.markdown("**Contact:** Loading...")
                st.markdown("**Summary:**")
                stx.scrollableTextbox("Loading...", height=250, border=False, key=id)

            st.markdown("---")

# Function to display actual profiles
def display_profiles(profiles: list[dict]):
    """Display the actual profiles fetched from the FastAPI server.

    Parameters
    ----------
    profiles : list[dict]
        The list of profiles to display.
    """
    search_results_placeholder.empty()
    
    with search_results_placeholder.container():
        for profile in profiles:
            col1, col2 = st.columns([1, 5])

            id = profile.get('url', 0).split('/')[-1]
            
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
                
                if 'url' in profile and profile['url']:
                    st.markdown(f"[View Full Profile]({profile['url']})", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"### {profile.get('name', 'N/A')}")
                st.markdown(f"**Department:** {profile.get('department', 'N/A')}")
                st.markdown(f"**Contact:** {profile.get('contact', 'N/A')}")
                st.markdown(f"**Summary:**")
                stx.scrollableTextbox(profile.get('summary', 'N/A'), height=250, border=False, key=id)
                
            st.markdown("---")  # Horizontal line for separation

# Search button
if search_button:
    # Display placeholders initially
    display_placeholders()
    
    # Fetch and display actual profiles
    profiles = get_profiles(query)
    if profiles:
        display_profiles(profiles)
