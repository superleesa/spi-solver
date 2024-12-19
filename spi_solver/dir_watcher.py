import time
from typing import Callable, Any

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent

IMG_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]


class DirectoryImageFileWatcher(FileSystemEventHandler):
    def __init__(self, callback: Callable[..., Any]) -> None:
        self.callback = callback

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        if not event.is_directory and any(
            [event.src_path.endswith(ext) for ext in IMG_EXTENSIONS]
        ):
            self.callback(event.src_path)


def watch_directory(path: str, callback: Callable[..., Any]) -> None:
    """
    Watch a directory for new image files and call the provided callback function when a new file is detected.
    
    Args:
        path (str): The path to the directory to watch.
        callback (Callable[..., Any]): The callback function to call when a new image file is
    """
    event_handler = DirectoryImageFileWatcher(callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def start_watching(screenshot_dir: str, image_queue: list[str]) -> None:
    """
    Start watching the specified directory for new image files and add them to the image queue.
    """
    def new_file_detected(filepath):
        image_queue.append(filepath)

    watch_directory(screenshot_dir, new_file_detected)
