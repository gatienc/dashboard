import os
import platform
import subprocess


def play_sound(file_path: str) -> None:
    """
    Play a sound file using the default system player.

    Args:
        file_path (str): The path to the sound file to play.

    Raises:
        FileNotFoundError: If the file does not exist.
        RuntimeError: If the sound could not be played.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Sound file not found: {file_path}")

    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", file_path], check=True)
        elif system == "Windows":
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
        else:  # Assume Linux/Unix
            subprocess.run(["ffplay", "-v", "0", "-nodisp",
                           "-autoexit", file_path], check=True)
    except Exception as e:
        raise RuntimeError(f"Failed to play sound: {e}")
