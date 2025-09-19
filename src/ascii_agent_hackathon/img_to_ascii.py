from typing import Optional, Tuple
from PIL import Image, ImageEnhance


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI escape code for 24-bit color."""
    return f"\033[38;2;{r};{g};{b}m"


def adjust_brightness(value: int, factor: float) -> int:
    """Adjust brightness of a value (0-255) by a factor."""
    return min(255, max(0, int(value * factor)))


def get_brightness_char(brightness: int, detailed: bool = True, invert: bool = False) -> str:
    """Get ASCII character based on brightness level."""
    if detailed:
        # More detailed character set for better gradients
        ascii_chars = " .·:¦+*#%@█"
    else:
        # Simple character set
        ascii_chars = " .:-=+*#%@"

    if invert:
        ascii_chars = ascii_chars[::-1]

    char_index = min(brightness * len(ascii_chars) // 256, len(ascii_chars) - 1)
    return ascii_chars[char_index]


def img_to_ascii(
    img_path: str,
    ascii_width: int = 200,
    ascii_height: int = 200,
    colored: bool = True,
    preserve_aspect_ratio: bool = True,
    detailed_chars: bool = True,
    brightness_boost: float = 1.5,
    contrast_boost: float = 1.2,
    invert_chars: bool = False
) -> str:
    """
    Convert an image to ASCII art.

    Args:
        img_path: Path to the input image
        ascii_width: Width of the ASCII output in characters
        ascii_height: Height of the ASCII output in characters (ignored if preserve_aspect_ratio=True)
        colored: Whether to use ANSI color codes for colored output
        preserve_aspect_ratio: Whether to maintain the original aspect ratio
        detailed_chars: Whether to use a more detailed character set
        brightness_boost: Factor to increase brightness (1.0 = no change, >1.0 = brighter)
        contrast_boost: Factor to increase contrast (1.0 = no change, >1.0 = more contrast)
        invert_chars: Whether to invert the character brightness mapping

    Returns:
        ASCII art representation of the image
    """
    try:
        img = Image.open(img_path)
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
            char = get_brightness_char(brightness, detailed_chars, invert_chars)

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
