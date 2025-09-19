from PIL import Image


def img_to_ascii(img_path: str, ascii_width: int = 200, ascii_height: int = 200) -> str:
    ascii_chars: str = "@%#*+=-:. "

    try:
        img = Image.open(img_path)
    except Exception as e:
        return f"Error opening image: {e}"

    img = img.convert('L')

    img = img.resize((ascii_width, ascii_height))

    pixels = img.getdata()

    ascii_str = ""
    for i, pixel in enumerate(pixels):
        char_index = pixel * len(ascii_chars) // 256
        ascii_str += ascii_chars[char_index]

        if (i + 1) % ascii_width == 0:
            ascii_str += "\n"

    return ascii_str
