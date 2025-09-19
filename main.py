# %%
from IPython.display import display

from ascii_agent_hackathon.img_to_ascii import display_ascii_animation, img_to_ascii
from ascii_agent_hackathon.LLM_gateway import generate_future_frame, generate_image

# %%

# Generate an image (will use cache if run multiple times)
generated_image = generate_image(
    "A cute golden retriever puppy playing in a sunny meadow. Pixel art style with very large pixels. 80x40 pixels.",
    save_path="images/generated_puppy.png",
    use_cache=True,  # Enable caching (default)
)

if generated_image:
    print("Image generated successfully!")
    # Display the generated image inline
    display(generated_image)

    # Show different character styles
    print("\n=== BLOCKS Style (Pixel-like █▓▒░) ===")
    blocks_ascii = img_to_ascii(
        "images/generated_puppy.png",
        ascii_width=80,
        colored=True,
        preserve_aspect_ratio=True,
        char_style="blocks",  # Block characters only
        brightness_boost=1.5,
        contrast_boost=1.2,
    )
    print(blocks_ascii)

    print("\n=== ASCII Style (Traditional @%#*+=:-.) ===")
    ascii_style = img_to_ascii(
        "images/generated_puppy.png",
        ascii_width=80,
        colored=True,
        preserve_aspect_ratio=True,
        char_style="ascii",  # ASCII characters only
        brightness_boost=1.5,
        contrast_boost=1.2,
    )
    print(ascii_style)

    print("\n=== MIXED Style (Default - Mix of both) ===")
    mixed_style = img_to_ascii(
        "images/generated_puppy.png",
        ascii_width=80,
        colored=True,
        preserve_aspect_ratio=True,
        char_style="mixed",  # Mix of ASCII and blocks
        brightness_boost=1.5,
        contrast_boost=1.2,
    )
    print(mixed_style)
else:
    print("Failed to generate image")

# %%
# Convert existing image to colored ASCII with brightness enhancement
print("\n=== Converting Red.jpeg to Colored ASCII (Blocks Style) ===")
colored_result = img_to_ascii(
    "images/Red.jpeg",
    ascii_width=100,
    colored=True,
    preserve_aspect_ratio=True,
    char_style="blocks",  # Use block characters for pixel-like appearance
    brightness_boost=1.8,  # More aggressive brightness for darker images
    contrast_boost=1.3,  # Higher contrast
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
        contrast_boost=1.2,
    )
    print(result[:300] + "...")  # Show just a preview

# %%
# Demonstrate caching - second call will use cached image
print("\n=== Cache Demonstration ===")
print("First call (generates new image):")
img1 = generate_image(
    "A majestic mountain landscape at sunset", save_path="images/mountain1.png"
)

print("\nSecond call with same prompt (uses cache):")
img2 = generate_image(
    "A majestic mountain landscape at sunset", save_path="images/mountain2.png"
)

print("\nThird call with use_cache=False (generates new):")
img3 = generate_image(
    "A majestic mountain landscape at sunset",
    save_path="images/mountain3.png",
    use_cache=False,
)

# %%
# Generate future frames - create a simple animation sequence
print("\n=== Future Frame Generation & Animation ===")
print("Generating a bouncing ball animation...")

# Generate initial frame
initial_image = generate_image(
    "A red ball in mid-air above a floor, about to fall. Simple clean illustration style.",
    save_path="images/ball_frame_0.png",
)

if initial_image:
    display(initial_image)
    print("Initial frame generated")

    # Generate future frames
    frames = [initial_image]
    for i in range(1, 6):  # Generate more frames for smoother animation
        time_offset = i * 0.3  # 0.3 second intervals
        print(f"\nGenerating frame at +{time_offset}s...")

        future_frame = generate_future_frame(
            frames[-1],  # Use the previous frame as input
            seconds_in_future=0.3,
            save_path=f"images/ball_frame_{i}.png",
        )

        if future_frame:
            display(future_frame)
            frames.append(future_frame)

    print("\n" + "=" * 50)
    print("All frames generated! Now playing as ASCII animation...")
    print("=" * 50)

    # %%
    # Play the animation!
    display_ascii_animation(
        frames,
        ascii_width=60,
        fps=3.0,  # 3 frames per second
        loop=True,
        loop_count=3,  # Loop 3 times
        colored=True,
        char_style="blocks",
        brightness_boost=1.8,
        contrast_boost=1.3,
        clear_terminal=False,  # Use IPython clear for Jupyter
    )

# %%
# Create a simple pendulum animation
print("\n=== Pendulum Animation ===")
pendulum_frames = []

# Generate pendulum frames
pendulum_prompts = [
    "A simple pendulum swinging to the left, black ball on a string against white background",
    "A simple pendulum at the center bottom position, black ball on a string against white background",
    "A simple pendulum swinging to the right, black ball on a string against white background",
    "A simple pendulum at the center bottom position, black ball on a string against white background",
]

for i, prompt in enumerate(pendulum_prompts):
    print(f"Generating pendulum frame {i + 1}/{len(pendulum_prompts)}...")
    frame = generate_image(prompt, save_path=f"images/pendulum_{i}.png")
    if frame:
        pendulum_frames.append(frame)

# %%

# %%
if pendulum_frames:
    print("\nPlaying pendulum animation...")
    display_ascii_animation(
        pendulum_frames,
        ascii_width=50,
        fps=2.0,
        loop=True,
        loop_count=5,
        colored=True,
        char_style="blocks",  # Use ASCII style for this one
        brightness_boost=1.5,
    )

# %%
