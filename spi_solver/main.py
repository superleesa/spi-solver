import time
import threading
import os
import platform

import streamlit as st
import fire

from spi_solver.dir_watcher import start_watching
from spi_solver.solvers.chatgpt import OpenAIImageAnalyzer


st.title("SPI Solver")
placeholder = st.empty()

def main(screenshot_dir: str | None) -> None:
    if screenshot_dir is None:
        if platform.system() == "Windows":
            screenshot_dir = os.path.join(os.environ["USERPROFILE"], "Pictures", "Screenshots")
        else:
            # TODO: enable setting the default screenshot dir using env var
            raise ValueError("Please provide the path to the directory to watch for new images.")
    
    analyzer = OpenAIImageAnalyzer()
    image_queue = []
    
    # TODO: currently, watching screenshot dir is only suuported; support watching clipboards
    thread = threading.Thread(target=start_watching, args=(screenshot_dir, image_queue), daemon=True)
    thread.start()

    with placeholder.container():
        st.write("Watching directory for changes...")
        while True:
            if image_queue:
                image_path = image_queue.pop(0)
                st.write_stream(analyzer.ask_about_picture(image_path))
            else:
                time.sleep(1)

if __name__ == "__main__":
    fire.Fire(main)
