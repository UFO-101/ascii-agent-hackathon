# %%
from IPython.display import display

from ascii_agent_hackathon.img_to_ascii import (
    create_character_animation,
    display_ascii_animation,
    display_smooth_ascii_animation,
    display_ultra_smooth_ascii_animation,
    img_to_ascii,
)
from ascii_agent_hackathon.LLM_gateway import generate_character_pose, generate_image

# %%
# Character Animation - Generate different poses of Red and interpolate between them
print("\n=== Character Pose Animation (Debug Mode) ===")
print("Creating an animation of the Red character with different poses...")
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

base_red = "images/Comp.jpg"

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

pose4 = generate_character_pose(
    # base_red, "surprised face", save_path="images/red_simple_pose4.png"
    base_red,
    "surprised face, tongue out",
    save_path="images/red_simple_pose4.png",
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
    print("Pose 4: Surprised face")
    display(pose4)
    # %%

    # Create interpolated frames
    from ascii_agent_hackathon.img_to_ascii import (
        create_interpolated_frames,
        display_image_animation,
    )

    interpolated = create_interpolated_frames(
        [pose1, pose2, pose3, pose4], frames_between=6, loop_back=True, debug=True
    )

    print(f"\n" + "=" * 40)
    print(f"Interpolated Animation ({len(interpolated)} frames)")
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
    print("\nUsing ultra-smooth ANSI animation...")
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
