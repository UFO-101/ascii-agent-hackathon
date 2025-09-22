# %%
from IPython.display import display

from ascii_agent_hackathon.img_to_ascii import (
    create_character_animation,
    display_ascii_animation,
    display_smooth_ascii_animation,
    display_ultra_smooth_ascii_animation,
    img_to_ascii,
)
from ascii_agent_hackathon.LLM_gateway import (
    generate_character_pose,
    generate_character_with_speech_bubble,
    generate_image,
)

# %%
# Get user input for speech bubble
print("=" * 60)
print("🎬 CHARACTER ANIMATION WITH SPEECH BUBBLE")
print("=" * 60)
print("This will create an animated character that speaks your message!")
print()

user_text = input("Enter text for the character to say: ").strip()
if not user_text:
    user_text = "Hello there!"  # Default text

print(f"\n✓ Character will say: '{user_text}'")
print()

# Character Animation - Generate different poses of Red and interpolate between them
print("=== Character Pose Animation (Debug Mode) ===")
print("Creating an animation of the character with different poses...")
print("This will show each stage: poses → interpolation → ASCII animation")

# Define different poses for the character
character_poses = [
    "eyes closed",
    "eyes look to the left",
    "eyes look to the right",
]

# Create the complete character animation with debugging enabled
# create_character_animation(
#     base_image="images/Red.jpeg",
#     poses=character_poses,
#     frames_between=3,  # 3 interpolated frames between each pose
#     ascii_width=50,
#     debug=True,  # Enable debugging to see each stage
#     fps=4.0,
#     loop=True,
#     loop_count=2,
#     colored=True,
#     char_style="blocks",
#     brightness_boost=1.8,
#     contrast_boost=1.3,
# )

# %%
# Simple 2-pose demonstration for detailed inspection
print("\n=== Simple 2-Pose Demo (Detailed) ===")
print("Creating a simple animation between just 2 poses...")

# base_red = "images/Comp.jpg"
# base_red = "images/Comp2.jpeg"
base_red = "images/Comp3.jpg"
# base_red = "images/Comp4.jpg"
# base_red = "images/Red.jpeg"

# Generate 2 contrasting poses
print("Generating pose 1...")
pose1 = generate_character_pose(
    base_red, "eyes closed", save_path="images/red_simple_pose1.png"
)

print("Generating pose 2...")
pose2 = generate_character_pose(
    base_red, "eyes look to the right", save_path="images/red_simple_pose2.png"
)

pose3 = generate_character_pose(
    base_red, "eyes looking up", save_path="images/red_simple_pose3.png"
)

# Generate speech bubble pose with user's text
print("Generating speech bubble pose...")
pose4 = generate_character_with_speech_bubble(
    base_red,
    user_text,
    save_path="images/red_speech_bubble.png",
)
pose5 = generate_character_pose(
    base_red, "surprised face, tongue out", save_path="images/red_simple_pose3.png"
)

# %%

if pose1 and pose2:
    print("\n" + "=" * 40)
    print("Original poses:")
    print("=" * 40)
    print("Pose 1: Eyes closed")
    display(pose1)

    print("Pose 2: Eyes look to the right")
    display(pose2)
    print("Pose 3: Eyes looking up")
    display(pose3)
    print(f"Pose 4: Speaking - '{user_text}'")
    display(pose4)
    # %%

    # Create interpolated frames
    from ascii_agent_hackathon.img_to_ascii import (
        create_interpolated_frames,
        display_image_animation,
    )

    interpolated = create_interpolated_frames(
        [pose1, pose2, pose3, pose4, pose5],
        frames_between=6,
        loop_back=True,
        debug=True,
    )

    print(f"\n" + "=" * 40)
    print(f"Interpolated Animation ({len(interpolated)} frames)")
    print(
        f"🗨️  Animation sequence: eyes closed → eyes right → eyes up → SPEAKING: '{user_text}' → loop"
    )
    print("=" * 40)
    print("Playing interpolated frames as images...")

    display_image_animation(interpolated, fps=6.0, loop_count=1)

    print("\n" + "=" * 40)
    print("ASCII Animation")
    print("=" * 40)

    # %%
    print("Choose animation method:")
    print("1. Terminal clearing (smooth)")
    print("2. ANSI escape codes (ultra-smooth)")
    print("3. IPython clear_output (original)")

    # Use ultra-smooth for best performance
    print(f"\n🎭 Starting ASCII animation with speech bubble: '{user_text}'...")
    display_ultra_smooth_ascii_animation(
        interpolated,
        ascii_width=120,
        fps=10.0,
        loop_count=4,
        colored=True,
        char_style="blocks",
        brightness_boost=1.3,
        contrast_boost=1.1,
    )

    print(f"\n🎉 Animation complete! Your character said: '{user_text}'")
    print("💬 The speech bubble was included in the 4th pose of the animation loop!")

    # print("\nAlternatively, try terminal clearing...")
    # display_smooth_ascii_animation(
    #     interpolated,
    #     ascii_width=60,
    #     fps=8.0,
    #     loop_count=1,
    #     colored=True,
    #     char_style="blocks",
    #     brightness_boost=1.8,
    # )

# %%
