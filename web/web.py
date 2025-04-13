import streamlit as st

class Main():
    def __init__(self):
        pg = st.navigation([
            st.Page(self.main, title="Main", icon="🏠"),
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
        st.header("Main", divider="rainbow")

    # Function to Display Body
    def body(self):
        st.image("web/jek.jpg", caption="J3K")

    # Function to Display Sidebar
    def sidebar(self):
        with st.sidebar:
            st.button("Start")

if __name__ == '__main__':
    main = Main()
