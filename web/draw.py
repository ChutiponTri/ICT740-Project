import streamlit as st
from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_ctx
from streamlit_drawable_canvas import st_canvas
from threading import Thread
from io import BytesIO
from PIL import Image
from api import API
import queue

class Draw():
    result_queue = queue.Queue()
    def __init__(self):
        self.header()
        self.sidebar()
        self.body()
    
    # Function to Display Header
    def header(self):
        st.header("Draw", divider="rainbow")

    # Function to Display Sidebar
    def sidebar(self):
        with st.sidebar:
            # Brush options
            self.stroke_width = st.slider("Brush size", 1, 25, 5)
            self.stroke_color = st.color_picker("Brush color", "#000000")
            self.bg_color = st.color_picker("Background color", "#ffffff")

    # Function to Display Body
    def body(self):
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",  # Transparent fill
            stroke_width=self.stroke_width,
            stroke_color=self.stroke_color,
            background_color=self.bg_color,
            height=500,
            width=500,
            drawing_mode="freedraw",
            key="canvas",
        )

        columns = st.columns([0.2, 0.2, 1.2])
        pred_button = columns[0].button("Predict")
        reset_button = columns[1].button("Reset")
        if pred_button and canvas_result.image_data is not None:
            st.session_state["waiting"] = True  # signal start
            image_pil = Image.fromarray((canvas_result.image_data).astype("uint8"))
            image_pil = image_pil.convert("L")
            byte_io = BytesIO()
            image_pil.save(byte_io, format="PNG")
            byte_io.seek(0)
            task = Thread(target=API.post, args=(byte_io, self.result_queue))
            task.start()
            add_script_run_ctx(task)

        # 🟡 Non-blocking check
        if "waiting" in st.session_state and st.session_state["waiting"]:
            try:
                result = self.result_queue.get()
                st.session_state["result"] = result
                st.session_state["waiting"] = False
            except queue.Empty:
                st.info("Predicting... please wait.")

        # ✅ Show result if available
        if "result" in st.session_state and not st.session_state.get("waiting", False):
            if "prediction" in st.session_state['result'].keys():
                st.success(f"Prediction result: {st.session_state['result']['prediction']}")
            else:
                st.success(f"Prediction result: {st.session_state['result']}")

        if reset_button:
            if "result" in st.session_state:
                del st.session_state["result"]
            if "waiting" in st.session_state:
                del st.session_state["waiting"]
            st.rerun()

draw = Draw()