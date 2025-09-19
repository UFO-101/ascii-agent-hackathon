# %%
from IPython.display import display

from ascii_agent_hackathon.img_to_ascii import img_to_ascii
from ascii_agent_hackathon.LLM_gateway import generate_image

# Generate an image
generated_image = generate_image(
    "A cute golden retriever puppy playing in a sunny meadow. Pixel art style with very large pixels. 80x40 pixels.",
    save_path="images/generated_puppy.png",
)

if generated_image:
    print("Image generated successfully!")
    # Display the generated image inline
    display(generated_image)
    # Convert the generated image to ASCII
    ascii_art = img_to_ascii(
        "images/generated_puppy.png", ascii_width=80, ascii_height=40
    )
    print(ascii_art)
else:
    print("Failed to generate image")

# Convert existing image to ASCII
result = img_to_ascii("images/Red.jpeg", ascii_width=80, ascii_height=40)
print(result)

# %%
