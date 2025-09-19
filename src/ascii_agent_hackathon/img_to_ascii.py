import time
import os
from typing import Optional, Tuple, Union, List
from IPython.display import clear_output, display
from PIL import Image, ImageEnhance


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI escape code for 24-bit color."""
    return f"\033[38;2;{r};{g};{b}m"


def adjust_brightness(value: int, factor: float) -> int:
    """Adjust brightness of a value (0-255) by a factor."""
    return min(255, max(0, int(value * factor)))


def get_brightness_char(brightness: int, style: str = "mixed", invert: bool = False) -> str:
    """
    Get ASCII character based on brightness level.

    Args:
        brightness: Brightness value (0-255)
        style: Character style - "blocks", "ascii", or "mixed"
        invert: Whether to invert the character brightness mapping
    """
    if style == "blocks":
        # Pure block/pixel characters for consistent pixel-like appearance
        ascii_chars = " ░▒▓█"  # Unicode block characters
        # Alternative: " ▪▫■□▢▣▤▥▦▧▨▩"
    elif style == "ascii":
        # Traditional ASCII characters only (no Unicode blocks)
        ascii_chars = " .:-=+*#%@"
    else:  # mixed (default)
        # Mix of ASCII and block characters
        ascii_chars = " .·:¦+*#%@█"

    if invert:
        ascii_chars = ascii_chars[::-1]

    char_index = min(brightness * len(ascii_chars) // 256, len(ascii_chars) - 1)
    return ascii_chars[char_index]


def img_to_ascii(
    img_source: Union[str, Image.Image],
    ascii_width: int = 200,
    ascii_height: int = 200,
    colored: bool = True,
    preserve_aspect_ratio: bool = True,
    char_style: str = "mixed",
    brightness_boost: float = 1.5,
    contrast_boost: float = 1.2,
    invert_chars: bool = False
) -> str:
    """
    Convert an image to ASCII art.

    Args:
        img_source: Either a path to the input image or a PIL Image object
        ascii_width: Width of the ASCII output in characters
        ascii_height: Height of the ASCII output in characters (ignored if preserve_aspect_ratio=True)
        colored: Whether to use ANSI color codes for colored output
        preserve_aspect_ratio: Whether to maintain the original aspect ratio
        char_style: Character style - "blocks" (█▓▒░), "ascii" (@%#*+=:-.), or "mixed" (both)
        brightness_boost: Factor to increase brightness (1.0 = no change, >1.0 = brighter)
        contrast_boost: Factor to increase contrast (1.0 = no change, >1.0 = more contrast)
        invert_chars: Whether to invert the character brightness mapping

    Returns:
        ASCII art representation of the image
    """
    try:
        if isinstance(img_source, str):
            img = Image.open(img_source)
        elif isinstance(img_source, Image.Image):
            img = img_source
        else:
            return f"Error: Invalid image source type: {type(img_source)}"
    except Exception as e:
        return f"Error opening image: {e}"

    # Apply brightness and contrast enhancements
    if brightness_boost != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness_boost)

    if contrast_boost != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_boost)

    # Get original dimensions
    orig_width, orig_height = img.size

    # Calculate height based on aspect ratio if requested
    # Note: Characters are typically ~2x taller than wide, so we compensate
    if preserve_aspect_ratio:
        aspect_ratio = orig_height / orig_width
        ascii_height = int(ascii_width * aspect_ratio * 0.5)  # 0.5 compensates for character aspect

    # Resize image
    img_resized = img.resize((ascii_width, ascii_height), Image.Resampling.LANCZOS)

    # Convert to RGB for color processing
    img_rgb = img_resized.convert('RGB')

    # Also get grayscale for brightness
    img_gray = img_resized.convert('L')

    ascii_str = ""

    for y in range(ascii_height):
        for x in range(ascii_width):
            # Get pixel values
            brightness = img_gray.getpixel((x, y))
            char = get_brightness_char(brightness, char_style, invert_chars)

            if colored:
                r, g, b = img_rgb.getpixel((x, y))
                # Optional: Also boost color brightness
                if brightness_boost > 1.0:
                    r = adjust_brightness(r, brightness_boost * 0.7)  # Less aggressive on colors
                    g = adjust_brightness(g, brightness_boost * 0.7)
                    b = adjust_brightness(b, brightness_boost * 0.7)
                # Add color code before character
                ascii_str += rgb_to_ansi(r, g, b) + char
            else:
                ascii_str += char

        # Reset color at end of line if using colors
        if colored:
            ascii_str += "\033[0m"
        ascii_str += "\n"

    # Final color reset for safety
    if colored:
        ascii_str += "\033[0m"

    return ascii_str


def display_ascii_animation(
    frames: List[Union[str, Image.Image]],
    ascii_width: int = 80,
    ascii_height: int = 40,
    fps: float = 10.0,
    loop: bool = True,
    loop_count: int = 3,
    colored: bool = True,
    char_style: str = "blocks",
    brightness_boost: float = 1.5,
    contrast_boost: float = 1.2,
    clear_terminal: bool = False
) -> None:
    """
    Display a sequence of images as an ASCII animation.

    Args:
        frames: List of image paths or PIL Image objects to animate
        ascii_width: Width of ASCII frames in characters
        ascii_height: Height of ASCII frames (ignored if preserve_aspect_ratio=True in conversion)
        fps: Frames per second for animation playback
        loop: Whether to loop the animation
        loop_count: Number of times to loop (if loop=True)
        colored: Whether to use colored ASCII art
        char_style: Character style - "blocks", "ascii", or "mixed"
        brightness_boost: Brightness adjustment factor
        contrast_boost: Contrast adjustment factor
        clear_terminal: If True, clears entire terminal; if False, uses IPython clear_output
    """
    if not frames:
        print("No frames to animate!")
        return

    # Pre-convert all frames to ASCII to avoid conversion delay during playback
    print(f"Converting {len(frames)} frames to ASCII...")
    ascii_frames = []
    for i, frame in enumerate(frames):
        print(f"Processing frame {i+1}/{len(frames)}...", end='\r')
        ascii_frame = img_to_ascii(
            frame,
            ascii_width=ascii_width,
            ascii_height=ascii_height,
            colored=colored,
            preserve_aspect_ratio=True,
            char_style=char_style,
            brightness_boost=brightness_boost,
            contrast_boost=contrast_boost
        )
        ascii_frames.append(ascii_frame)

    print("\nStarting animation playback...")
    time.sleep(1)  # Brief pause before starting

    frame_delay = 1.0 / fps
    loops_completed = 0

    try:
        while True:
            for frame_num, ascii_frame in enumerate(ascii_frames):
                if clear_terminal:
                    # Clear entire terminal screen
                    os.system('clear' if os.name == 'posix' else 'cls')
                else:
                    # Use IPython's clear_output for Jupyter environments
                    clear_output(wait=True)

                # Display the frame
                print(f"Frame {frame_num + 1}/{len(frames)} | Loop {loops_completed + 1}/{loop_count if loop else 1}")
                print(ascii_frame)

                # Wait for next frame
                time.sleep(frame_delay)

            loops_completed += 1

            if not loop or (loop_count > 0 and loops_completed >= loop_count):
                break

        print(f"\nAnimation complete! Played {loops_completed} loop(s).")

    except KeyboardInterrupt:
        print("\nAnimation interrupted by user.")


def create_ascii_animation_frames(
    images: List[Union[str, Image.Image]],
    ascii_width: int = 80,
    **kwargs
) -> List[str]:
    """
    Pre-convert images to ASCII frames for animation.

    Args:
        images: List of image paths or PIL Image objects
        ascii_width: Width of ASCII output
        **kwargs: Additional arguments to pass to img_to_ascii

    Returns:
        List of ASCII art strings
    """
    ascii_frames = []
    for img in images:
        ascii_frame = img_to_ascii(
            img,
            ascii_width=ascii_width,
            preserve_aspect_ratio=True,
            **kwargs
        )
        ascii_frames.append(ascii_frame)
    return ascii_frames
