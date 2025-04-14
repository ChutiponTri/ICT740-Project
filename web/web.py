import streamlit as st

class Main():
    def __init__(self):
        pg = st.navigation([
            st.Page(self.main, title="Home", icon="🏠"),
            st.Page("draw.py", title="Draw", icon="🖌️"),
            st.Page("camera.py", title="Camera", icon="📷"),
        ])
        pg.run()

    # Function to Display Main 
    def main(self):
        self.header()
        self.sidebar()
        self.body()
        
    # Function to Display Header
    def header(self):
        st.header("Draw Anything. Let AI Guess. Have Fun", divider="rainbow")

    # Function to Display Body
    def body(self):
        # st.image("web/jek.jpg", caption="J3K")
        st.image("web/welcome.png")
        st.markdown("""
        **Welcome to a playful AI-powered experience where creativity meets intelligence.**  
        Just sketch your idea, and let our cheerful little robot try to guess what it is!  
        Whether it’s a doodle or a masterpiece, every drawing is a chance to test the AI’s smarts and have some fun while you're at it!
        """)
    # Function to Display Sidebar
    def sidebar(self):
        with st.sidebar:
            if st.button("Start"):
                st.switch_page("draw.py")

if __name__ == '__main__':
    main = Main()
