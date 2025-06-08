# --- Page State Management for Sidebar Navigation ---
# Ensure 'page' is initialized.
# This makes sure that if the app restarts or for the very first load,
# 'home' is the default and is in the list of options.
if 'page' not in st.session_state or st.session_state.page not in [
    "Home", "Upload Data", "Dashboard Overview", "Headline Analysis",
    "Keyword Trends", "Sentiment Over Time", "Source Performance",
    "Media Reach", "Settings", "Help"
]:
    st.session_state.page = 'Home' # Set a default page that is definitely in the list

# --- Sidebar Content ---
st.sidebar.title("MENU ANALISIS")

# Define the list of page options.
# Keep this list consistent with all logic that sets st.session_state.page
page_options = [
    "Home",
    "Upload Data",
    "Dashboard Overview",
    "Headline Analysis",
    "Keyword Trends",
    "Sentiment Over Time",
    "Source Performance",
    "Media Reach",
    "Settings",
    "Help"
]

# Get the current index of the selected page
try:
    current_page_index = page_options.index(st.session_state.page)
except ValueError:
    # Fallback in case st.session_state.page somehow gets an invalid value
    current_page_index = 0 # Default to 'Home'
    st.session_state.page = page_options[current_page_index] # Correct the session state

# Custom navigation using st.radio for "capsule" style
page_selection = st.sidebar.radio(
    "Navigasi",
    page_options,
    index=current_page_index, # Use the calculated index
    key="main_navigation"
)

# Update session state if the user selects a different page from the radio button
if page_selection:
    st.session_state.page = page_selection

# --- Main Content Area ---
# ... (rest of your app code remains the same)
