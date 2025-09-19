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

    # Convert with colored ASCII art (with brightness boost!)
    print("\n=== Colored ASCII Art (Brightness Enhanced) ===")
    colored_ascii = img_to_ascii(
        "images/generated_puppy.png",
        ascii_width=80,
        colored=True,
        preserve_aspect_ratio=True,
        detailed_chars=True,
        brightness_boost=1.5,  # Increase brightness by 50%
        contrast_boost=1.2     # Slight contrast boost
    )
    print(colored_ascii)

    # Also show grayscale version for comparison
    print("\n=== Grayscale ASCII Art (Brightness Enhanced) ===")
    grayscale_ascii = img_to_ascii(
        "images/generated_puppy.png",
        ascii_width=80,
        colored=False,
        preserve_aspect_ratio=True,
        detailed_chars=True,
        brightness_boost=1.5,  # Same brightness boost
        contrast_boost=1.2
    )
    print(grayscale_ascii)
else:
    print("Failed to generate image")

# %%
# Convert existing image to colored ASCII with brightness enhancement
print("\n=== Converting Red.jpeg to Colored ASCII (Brightness Enhanced) ===")
colored_result = img_to_ascii(
    "images/Red.jpeg",
    ascii_width=100,
    colored=True,
    preserve_aspect_ratio=True,
    detailed_chars=True,
    brightness_boost=1.8,  # More aggressive brightness for darker images
    contrast_boost=1.3     # Higher contrast
)
print(colored_result)

# %%
# Show different brightness levels for comparison
print("\n=== Brightness Comparison ===")
for brightness in [1.0, 1.5, 2.0]:
    print(f"\nBrightness Factor: {brightness}")
    result = img_to_ascii(
        "images/Red.jpeg",
        ascii_width=60,
        colored=True,
        preserve_aspect_ratio=True,
        brightness_boost=brightness,
        contrast_boost=1.2
    )
    print(result[:300] + "...")  # Show just a preview

# %%
