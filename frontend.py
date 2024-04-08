import io
import streamlit as st
import streamlit_scrollable_textbox as stx
import requests
import logging
import random

from src.LoggerFormatter import CustomFormatter

# Set the endpoint
ENDPOINT = "http://backend:8000/profiles"
DEFAULT_IMAGE = "https://static.vecteezy.com/system/resources/previews/032/176/017/original/business-avatar-profile-black-icon-man-of-user-symbol-in-trendy-flat-style-isolated-on-male-profile-people-diverse-face-for-social-network-or-web-vector.jpg"

# Set up logging
logging.basicConfig(level=logging.INFO)
logging.getLogger().handlers[0].setFormatter(CustomFormatter())  # Set custom formatter

# Set page config
st.set_page_config(page_title="Staff Finder", page_icon="🎓")

# This is a workaround to hide the Streamlit menu and footer
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

# Streamlit app layout
st.title("🎓Imperial College Staff Finder")

# Search bar
query = st.text_input("Enter topics you're looking for:")

col1, col2, col3 = st.columns([1,1,1])
# Search button
with col1:
    quick_search_button = st.button("Quick Search", disabled=False, use_container_width=True)
with col2:
    norm_search_button = st.button("Normal Search", disabled=False, use_container_width=True)
with col3:
    long_search_button = st.button("Long Search", disabled=True, use_container_width=True)

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
                st.image(DEFAULT_IMAGE, width=150, use_column_width=True) # Default image

            with col2:
                # Placeholder for profile information
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
    search_results_placeholder.empty()  # Clear the placeholders
    
    with search_results_placeholder.container():
        # Display each profile. They have the same structure as the placeholder
        ids: list[str] = []
        for profile in profiles:
            col1, col2 = st.columns([1, 5])

            id: str = profile.get('url', None)
            id = id.split("/")[-1] if id else random.randint(0, 1000)  # Generate a random ID if the URL is not available
            if id in ids:
                id = f"{id}_{random.randint(0, 1000)}"
            ids.append(id)
            
            with col1:
                if 'url' in profile and profile['url']:

                    try:
                        img_data = requests.get(f"{profile['url']}/portrait.jpg").content
                        with io.BytesIO(img_data) as f: # Open a file-like buffer
                            f.seek(0)
                            st.image(f, width=150, use_column_width=True)

                    except Exception as e:
                        img_data = DEFAULT_IMAGE
                        st.image(img_data, width=150, use_column_width=True)

                else:
                    st.image(DEFAULT_IMAGE, width=150, use_column_width=True)
                
                if 'url' in profile and profile['url']:
                    st.markdown(f"[View Full Profile]({profile['url']})", unsafe_allow_html=True)   # Link to full profile
            
            with col2:
                # Display profile information
                st.markdown(f"### {profile.get('name', 'N/A')}")
                st.markdown(f"**Department:** {profile.get('department', 'N/A')}")
                st.markdown(f"**Contact:** {profile.get('contact', 'N/A')}")
                st.markdown(f"**Summary:**")
                stx.scrollableTextbox(profile.get('summary', 'N/A'), height=250, border=False, key=id)
                
            st.markdown("---")  # Horizontal line for separation

# Function to send POST request to the FastAPI server
def get_profiles(query: str, method: str = "/norm") -> list[dict] | None:
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
        response = requests.post(ENDPOINT+method, json={"query": query})   # Send POST request
        if response.status_code == 200:                             # Check if the request is successful
            return response.json()['profiles']

    except Exception as e:
        logging.error(f"Failed to retrieve profiles: {e}")
        pass

    search_results_placeholder.empty()
    return None

# Search button
if quick_search_button or norm_search_button or long_search_button:
    # Display placeholders initially
    display_placeholders()

    # Determine the search method based on the button clicked
    if quick_search_button:
        method = "/quick"
    elif norm_search_button:
        method = "/norm"
    elif long_search_button:
        method = "/long"
    
    # Fetch and display actual profiles
    profiles = get_profiles(query, method=method)
    if profiles:
        display_profiles(profiles)
    else:
        st.error("Failed to retrieve profiles. Please try again.")
