import os
import time
from typing import List, Optional, Tuple, Union

import numpy as np
from IPython.display import clear_output, display
from PIL import Image, ImageEnhance


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI escape code for 24-bit color."""
    return f"\033[38;2;{r};{g};{b}m"


def adjust_brightness(value: int, factor: float) -> int:
    """Adjust brightness of a value (0-255) by a factor."""
    return min(255, max(0, int(value * factor)))


def get_brightness_char(
    brightness: int, style: str = "mixed", invert: bool = False
) -> str:
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
    invert_chars: bool = False,
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
        ascii_height = int(
            ascii_width * aspect_ratio * 0.5
        )  # 0.5 compensates for character aspect

    # Resize image
    img_resized = img.resize((ascii_width, ascii_height), Image.Resampling.LANCZOS)

    # Convert to RGB for color processing
    img_rgb = img_resized.convert("RGB")

    # Also get grayscale for brightness
    img_gray = img_resized.convert("L")

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
                    r = adjust_brightness(
                        r, brightness_boost * 0.7
                    )  # Less aggressive on colors
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
    clear_terminal: bool = False,
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
        print(f"Processing frame {i + 1}/{len(frames)}...", end="\r")
        ascii_frame = img_to_ascii(
            frame,
            ascii_width=ascii_width,
            ascii_height=ascii_height,
            colored=colored,
            preserve_aspect_ratio=True,
            char_style=char_style,
            brightness_boost=brightness_boost,
            contrast_boost=contrast_boost,
        )
        ascii_frames.append(ascii_frame)

    print("\nStarting animation playback...")
    time.sleep(0.5)  # Brief pause before starting

    frame_delay = 1.0 / fps
    loops_completed = 0

    try:
        while True:
            for frame_num, ascii_frame in enumerate(ascii_frames):
                # More aggressive clearing for smoother animation
                if clear_terminal:
                    # Clear entire terminal screen
                    os.system("clear" if os.name == "posix" else "cls")
                else:
                    # Use IPython's clear_output for Jupyter environments
                    clear_output(wait=True)

                # Minimize extra output to reduce flicker
                if frame_num == 0 and loops_completed == 0:
                    # Show info only on first frame
                    print(f"Playing ASCII Animation - {len(frames)} frames, {fps} fps")

                # Display the frame immediately
                print(ascii_frame, end='', flush=True)

                # Wait for next frame with more precise timing
                time.sleep(max(0.01, frame_delay))  # Minimum 10ms delay

            loops_completed += 1

            if not loop or (loop_count > 0 and loops_completed >= loop_count):
                break

        # Final clear and completion message
        if not clear_terminal:
            clear_output(wait=True)
        print(f"Animation complete! Played {loops_completed} loop(s).")

    except KeyboardInterrupt:
        if not clear_terminal:
            clear_output(wait=True)
        print("Animation interrupted by user.")


def display_smooth_ascii_animation(
    frames: List[Union[str, Image.Image]],
    ascii_width: int = 80,
    fps: float = 10.0,
    loop_count: int = 3,
    colored: bool = True,
    char_style: str = "blocks",
    brightness_boost: float = 1.5,
    contrast_boost: float = 1.2,
) -> None:
    """
    Display ASCII animation optimized for smoothness using terminal clearing.

    Args:
        frames: List of image paths or PIL Image objects to animate
        ascii_width: Width of ASCII frames in characters
        fps: Frames per second for animation playback
        loop_count: Number of times to loop the animation
        colored: Whether to use colored ASCII art
        char_style: Character style - "blocks", "ascii", or "mixed"
        brightness_boost: Brightness adjustment factor
        contrast_boost: Contrast adjustment factor
    """
    if not frames:
        print("No frames to animate!")
        return

    # Pre-convert all frames to ASCII
    print(f"Pre-converting {len(frames)} frames for smooth playback...")
    ascii_frames = []
    for i, frame in enumerate(frames):
        ascii_frame = img_to_ascii(
            frame,
            ascii_width=ascii_width,
            colored=colored,
            preserve_aspect_ratio=True,
            char_style=char_style,
            brightness_boost=brightness_boost,
            contrast_boost=contrast_boost,
        )
        ascii_frames.append(ascii_frame)

    # Calculate frame timing
    frame_delay = 1.0 / fps

    print(f"Starting smooth animation: {len(frames)} frames @ {fps} fps")
    print("Press Ctrl+C to stop animation early")
    time.sleep(1)

    # Use terminal clearing for smoothest animation
    import sys

    try:
        for loop_num in range(loop_count):
            for frame_num, ascii_frame in enumerate(ascii_frames):
                # Clear terminal screen completely
                os.system("clear" if os.name == "posix" else "cls")

                # Display frame info and ASCII art
                print(f"ASCII Animation | Loop {loop_num+1}/{loop_count} | Frame {frame_num+1}/{len(frames)}")
                print("-" * ascii_width)
                print(ascii_frame, end="")

                # Flush output immediately for smoothness
                sys.stdout.flush()

                # Sleep for precise timing
                time.sleep(frame_delay)

        # Final clear and completion message
        os.system("clear" if os.name == "posix" else "cls")
        print(f"✓ Animation complete! {loop_count} loops played successfully.")

    except KeyboardInterrupt:
        os.system("clear" if os.name == "posix" else "cls")
        print("Animation interrupted by user.")


def display_ultra_smooth_ascii_animation(
    frames: List[Union[str, Image.Image]],
    ascii_width: int = 80,
    fps: float = 10.0,
    loop_count: int = 3,
    colored: bool = True,
    char_style: str = "blocks",
    brightness_boost: float = 1.5,
    contrast_boost: float = 1.2,
) -> None:
    """
    Display ASCII animation with ultra-smooth playback using ANSI escape codes.

    Args:
        frames: List of image paths or PIL Image objects to animate
        ascii_width: Width of ASCII frames in characters
        fps: Frames per second for animation playback
        loop_count: Number of times to loop the animation
        colored: Whether to use colored ASCII art
        char_style: Character style - "blocks", "ascii", or "mixed"
        brightness_boost: Brightness adjustment factor
        contrast_boost: Contrast adjustment factor
    """
    if not frames:
        print("No frames to animate!")
        return

    # Pre-convert all frames to ASCII
    print(f"Pre-converting {len(frames)} frames for ultra-smooth playback...")
    ascii_frames = []
    for i, frame in enumerate(frames):
        ascii_frame = img_to_ascii(
            frame,
            ascii_width=ascii_width,
            colored=colored,
            preserve_aspect_ratio=True,
            char_style=char_style,
            brightness_boost=brightness_boost,
            contrast_boost=contrast_boost,
        )
        ascii_frames.append(ascii_frame)

    # Calculate frame timing
    frame_delay = 1.0 / fps

    print(f"Starting ultra-smooth animation: {len(frames)} frames @ {fps} fps")
    print("Press Ctrl+C to stop animation early")
    time.sleep(1)

    # ANSI escape codes for ultra-fast clearing
    CLEAR_SCREEN = "\033[2J"    # Clear entire screen
    MOVE_CURSOR_HOME = "\033[H"  # Move cursor to top-left
    HIDE_CURSOR = "\033[?25l"    # Hide cursor for smoother display
    SHOW_CURSOR = "\033[?25h"    # Show cursor

    import sys

    try:
        # Hide cursor for smoother animation
        print(HIDE_CURSOR, end="", flush=True)

        for loop_num in range(loop_count):
            for frame_num, ascii_frame in enumerate(ascii_frames):
                # Ultra-fast clear using ANSI codes
                print(CLEAR_SCREEN + MOVE_CURSOR_HOME, end="", flush=True)

                # Display frame with minimal overhead
                print(f"ASCII Animation | Loop {loop_num+1}/{loop_count} | Frame {frame_num+1}/{len(frames)}")
                print(ascii_frame, end="", flush=True)

                # Precise timing
                time.sleep(frame_delay)

        # Final cleanup
        print(CLEAR_SCREEN + MOVE_CURSOR_HOME, end="", flush=True)
        print(SHOW_CURSOR, end="", flush=True)
        print(f"✓ Ultra-smooth animation complete! {loop_count} loops played.")

    except KeyboardInterrupt:
        # Cleanup on interrupt
        print(CLEAR_SCREEN + MOVE_CURSOR_HOME, end="", flush=True)
        print(SHOW_CURSOR, end="", flush=True)
        print("Animation interrupted by user.")


def create_ascii_animation_frames(
    images: List[Union[str, Image.Image]], ascii_width: int = 80, **kwargs
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
            img, ascii_width=ascii_width, preserve_aspect_ratio=True, **kwargs
        )
        ascii_frames.append(ascii_frame)
    return ascii_frames


def interpolate_images(
    img1: Image.Image, img2: Image.Image, alpha: float
) -> Image.Image:
    """
    Interpolate between two images using alpha blending.

    Args:
        img1: First image
        img2: Second image
        alpha: Interpolation factor (0.0 = img1, 1.0 = img2)

    Returns:
        Interpolated image
    """
    # Ensure both images are the same size
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

    # Convert to RGBA to ensure proper blending
    img1_rgba = img1.convert("RGBA")
    img2_rgba = img2.convert("RGBA")

    # Use PIL's built-in blend function
    return Image.blend(img1_rgba, img2_rgba, alpha).convert("RGB")


def create_interpolated_frames(
    poses: List[Image.Image], frames_between: int = 5, loop_back: bool = True, debug: bool = False
) -> List[Image.Image]:
    """
    Create interpolated frames between a set of pose images.

    Args:
        poses: List of pose images to interpolate between
        frames_between: Number of interpolated frames to create between each pair
        loop_back: Whether to interpolate back to the first pose at the end
        debug: If True, prints frame sequence information

    Returns:
        List of all frames including original poses and interpolated frames
    """
    if len(poses) < 2:
        return poses

    all_frames = []

    # Create interpolation sequence
    pose_pairs = []
    for i in range(len(poses) - 1):
        pose_pairs.append((poses[i], poses[i + 1]))

    # Add loop back to start if requested
    if loop_back:
        pose_pairs.append((poses[-1], poses[0]))

    if debug:
        print(f"Creating interpolation with {len(poses)} poses, {frames_between} frames between each")
        print(f"Pose pairs: {len(pose_pairs)} pairs")
        if loop_back:
            print("Loop back: YES - will return to first pose")
        else:
            print("Loop back: NO - will end on last pose")

    # Generate interpolated frames for each pair
    for pair_idx, (start_pose, end_pose) in enumerate(pose_pairs):
        if debug:
            print(f"Processing pair {pair_idx + 1}/{len(pose_pairs)}")

        # Add the starting pose
        all_frames.append(start_pose)

        # Create interpolated frames
        for frame_num in range(1, frames_between + 1):
            alpha = frame_num / (frames_between + 1)
            interpolated = interpolate_images(start_pose, end_pose, alpha)
            all_frames.append(interpolated)

    # Always add the final pose to complete the cycle
    if loop_back:
        # When looping back, add the first pose again to complete the cycle
        all_frames.append(poses[0])
        if debug:
            print("Added final frame: original first pose (completes loop)")
    else:
        # When not looping, add the final pose
        all_frames.append(poses[-1])
        if debug:
            print("Added final frame: last pose")

    if debug:
        print(f"Total frames created: {len(all_frames)}")

    return all_frames


def create_character_animation(
    base_image: Union[str, Image.Image],
    poses: List[str],
    frames_between: int = 5,
    ascii_width: int = 80,
    debug: bool = False,
    **animation_kwargs,
) -> None:
    """
    Create a character animation from a base image and pose descriptions.

    Args:
        base_image: Path to base character image or PIL Image
        poses: List of pose descriptions to generate
        frames_between: Number of interpolated frames between poses
        ascii_width: Width for ASCII conversion
        debug: If True, shows each stage of the process for debugging
        **animation_kwargs: Additional arguments for display_ascii_animation
    """
    from ascii_agent_hackathon.LLM_gateway import generate_character_pose

    print(f"Generating {len(poses)} character poses...")

    # Load base image
    if isinstance(base_image, str):
        base_img = Image.open(base_image)
    else:
        base_img = base_image

    # Show original image if debugging
    if debug:
        print("\n" + "=" * 50)
        print("STAGE 1: Original Base Image")
        print("=" * 50)
        display(base_img)

    # Generate all poses
    pose_images = [base_img]  # Start with original pose

    for i, pose_desc in enumerate(poses):
        print(f"Generating pose {i + 1}/{len(poses)}: {pose_desc}")
        pose_img = generate_character_pose(
            base_img, pose_desc, save_path=f"images/pose_{i + 1}.png"
        )
        if pose_img:
            pose_images.append(pose_img)

            # Show each generated pose if debugging
            if debug:
                print(f"\nPose {i + 1} generated: {pose_desc}")
                display(pose_img)

    if debug:
        print(f"\n" + "=" * 50)
        print("STAGE 2: All Generated Poses")
        print("=" * 50)
        print(f"Total poses: {len(pose_images)} (including original)")
        for i, pose_img in enumerate(pose_images):
            if i == 0:
                print(f"Original pose:")
            else:
                print(f"Pose {i}: {poses[i - 1]}")
            display(pose_img)

    print(f"\nCreating interpolated frames ({frames_between} between each pose)...")
    interpolated_frames = create_interpolated_frames(
        pose_images, frames_between=frames_between, loop_back=True
    )

    print(f"Total frames created: {len(interpolated_frames)}")

    if debug:
        print(f"\n" + "=" * 50)
        print("STAGE 3: Pixel Interpolation Animation")
        print("=" * 50)
        print("Playing interpolated frames as regular images...")

        # Show interpolated animation as regular images first
        display_image_animation(
            interpolated_frames,
            fps=animation_kwargs.get("fps", 5.0),
            loop_count=1,  # Just one loop for debugging
        )


def display_image_animation(
    frames: List[Image.Image], fps: float = 5.0, loop_count: int = 1
) -> None:
    """
    Display a sequence of PIL Images as an animation (not ASCII).

    Args:
        frames: List of PIL Image objects to animate
        fps: Frames per second for animation playback
        loop_count: Number of times to loop the animation
    """
    if not frames:
        print("No frames to animate!")
        return

    frame_delay = 1.0 / fps

    for loop in range(loop_count):
        for frame_num, frame in enumerate(frames):
            # clear_output(wait=True)
            print(f"Frame {frame_num + 1}/{len(frames)} | Loop {loop + 1}/{loop_count}")
            display(frame)
            time.sleep(frame_delay)

    print("Image animation complete!")
