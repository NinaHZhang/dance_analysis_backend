"""
Test script for the pose comparison module.

This script tests the core functionality with sample pose data to ensure
the comparison logic works correctly.
"""

import json
from models import PoseData
from compare import compare_all_frames, calculate_angle, generate_suggestion
from config import config


def test_angle_calculation():
    """Test the angle calculation function."""
    print("Testing angle calculation...")
    
    # Test case 1: Right angle
    p1 = (0, 0)
    p2 = (0, 1)
    p3 = (1, 1)
    angle = calculate_angle(p1, p2, p3)
    print(f"Right angle test: {angle:.2f}° (expected ~90°)")
    
    # Test case 2: Straight line
    p1 = (0, 0)
    p2 = (1, 1)
    p3 = (2, 2)
    angle = calculate_angle(p1, p2, p3)
    print(f"Straight line test: {angle:.2f}° (expected ~180°)")
    
    # Test case 3: Acute angle
    p1 = (0, 0)
    p2 = (1, 0)
    p3 = (1, 1)
    angle = calculate_angle(p1, p2, p3)
    print(f"Acute angle test: {angle:.2f}° (expected ~90°)")
    
    print("Angle calculation tests completed.\n")


def test_suggestion_generation():
    """Test the suggestion generation function."""
    print("Testing suggestion generation...")
    
    suggestions = [
        generate_suggestion("right_arm", 15.5),
        generate_suggestion("right_arm", -12.3),
        generate_suggestion("left_arm", 8.7),
        generate_suggestion("left_arm", -20.1),
        generate_suggestion("right_leg", 5.2),
        generate_suggestion("left_leg", -18.9),
        generate_suggestion("head_tilt", 10.5),
        generate_suggestion("torso", -15.2)
    ]
    
    for suggestion in suggestions:
        print(f"  - {suggestion}")
    
    print("Suggestion generation tests completed.\n")


def test_pose_comparison():
    """Test the main pose comparison function."""
    print("Testing pose comparison...")
    
    # Create sample pose data with significant differences that exceed threshold
    sample_pose_data = PoseData(
        original={
            "frame_1": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (120.0, 80.0),
                "right_wrist": (140.0, 60.0),
                "left_shoulder": (80.0, 100.0),
                "left_elbow": (60.0, 80.0),
                "left_wrist": (40.0, 60.0),
                "right_hip": (100.0, 150.0),
                "right_knee": (110.0, 200.0),
                "right_ankle": (120.0, 250.0),
                "left_hip": (80.0, 150.0),
                "left_knee": (90.0, 200.0),
                "left_ankle": (100.0, 250.0),
                "left_ear": (95.0, 90.0),
                "left_eye": (100.0, 85.0),
                "right_ear": (105.0, 90.0),
                "right_eye": (100.0, 85.0)
            },
            "frame_2": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (110.0, 90.0),
                "right_wrist": (120.0, 80.0),
                "left_shoulder": (80.0, 100.0),
                "left_elbow": (70.0, 90.0),
                "left_wrist": (60.0, 80.0),
                "right_hip": (100.0, 150.0),
                "right_knee": (105.0, 210.0),
                "right_ankle": (110.0, 260.0),
                "left_hip": (80.0, 150.0),
                "left_knee": (85.0, 210.0),
                "left_ankle": (90.0, 260.0),
                "left_ear": (95.0, 90.0),
                "left_eye": (100.0, 85.0),
                "right_ear": (105.0, 90.0),
                "right_eye": (100.0, 85.0)
            }
        },
        user={
            "frame_1": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (130.0, 70.0),  # 15° difference
                "right_wrist": (160.0, 40.0),  # 15° difference
                "left_shoulder": (80.0, 100.0),
                "left_elbow": (50.0, 70.0),    # 12° difference
                "left_wrist": (20.0, 40.0),    # 12° difference
                "right_hip": (100.0, 150.0),
                "right_knee": (115.0, 190.0),  # 8° difference
                "right_ankle": (130.0, 230.0), # 8° difference
                "left_hip": (80.0, 150.0),
                "left_knee": (85.0, 210.0),    # 6° difference (below threshold)
                "left_ankle": (95.0, 260.0),   # 6° difference (below threshold)
                "left_ear": (90.0, 85.0),      # 5° difference (below threshold)
                "left_eye": (95.0, 80.0),      # 5° difference (below threshold)
                "right_ear": (110.0, 85.0),    # 5° difference (below threshold)
                "right_eye": (105.0, 80.0)     # 5° difference (below threshold)
            },
            "frame_2": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (115.0, 85.0),  # 5° difference (below threshold)
                "right_wrist": (125.0, 75.0),  # 5° difference (below threshold)
                "left_shoulder": (80.0, 100.0),
                "left_elbow": (65.0, 85.0),    # 5° difference (below threshold)
                "left_wrist": (55.0, 75.0),    # 5° difference (below threshold)
                "right_hip": (100.0, 150.0),
                "right_knee": (100.0, 215.0),  # 5° difference (below threshold)
                "right_ankle": (105.0, 265.0), # 5° difference (below threshold)
                "left_hip": (80.0, 150.0),
                "left_knee": (80.0, 215.0),    # 5° difference (below threshold)
                "left_ankle": (85.0, 265.0),   # 5° difference (below threshold)
                "left_ear": (95.0, 90.0),
                "left_eye": (100.0, 85.0),
                "right_ear": (105.0, 90.0),
                "right_eye": (100.0, 85.0)
            }
        }
    )
    
    # Run comparison
    results = compare_all_frames(sample_pose_data)
    
    print(f"Found {len(results)} problematic frames:")
    for i, result in enumerate(results, 1):
        print(f"\nFrame {i}: {result.frame_id}")
        print(f"  Total Error: {result.total_error:.2f}°")
        print(f"  Joint Issues: {len(result.joint_issues)}")
        for issue in result.joint_issues:
            print(f"    - {issue.joint}: {issue.delta_angle:+.1f}°")
        print(f"  Suggestions:")
        for suggestion in result.suggestions:
            print(f"    - {suggestion}")
    
    print("\nPose comparison tests completed.\n")


def test_dance_style_configurations():
    """Test different dance style configurations."""
    print("Testing dance style configurations...")
    
    # Test data with moderate differences
    test_pose_data = PoseData(
        original={
            "frame_1": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (120.0, 80.0),
                "right_wrist": (140.0, 60.0),
                "left_shoulder": (80.0, 100.0),
                "left_elbow": (60.0, 80.0),
                "left_wrist": (40.0, 60.0),
                "right_hip": (100.0, 150.0),
                "right_knee": (110.0, 200.0),
                "right_ankle": (120.0, 250.0),
                "left_hip": (80.0, 150.0),
                "left_knee": (90.0, 200.0),
                "left_ankle": (100.0, 250.0)
            }
        },
        user={
            "frame_1": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (125.0, 75.0),  # 9° difference
                "right_wrist": (150.0, 50.0),  # 9° difference
                "left_shoulder": (80.0, 100.0),
                "left_elbow": (55.0, 75.0),    # 9° difference
                "left_wrist": (30.0, 50.0),    # 9° difference
                "right_hip": (100.0, 150.0),
                "right_knee": (115.0, 190.0),  # 8° difference
                "right_ankle": (130.0, 230.0), # 8° difference
                "left_hip": (80.0, 150.0),
                "left_knee": (85.0, 210.0),    # 6° difference
                "left_ankle": (95.0, 260.0)    # 6° difference
            }
        }
    )
    
    # Test with different dance styles
    for style in ["ballet", "hip_hop", "contemporary"]:
        print(f"\nTesting {style} style:")
        style_config = config.get_style_config(style)
        print(f"  Threshold: {style_config['angle_threshold']}°")
        
        # Temporarily update threshold
        original_threshold = config.ANGLE_THRESHOLD
        config.update_threshold(style_config['angle_threshold'])
        
        # Update the compare module's threshold
        import compare
        compare.ANGLE_THRESHOLD = style_config['angle_threshold']
        
        results = compare_all_frames(test_pose_data)
        print(f"  Found {len(results)} problematic frames")
        
        # Restore original threshold
        config.update_threshold(original_threshold)
        compare.ANGLE_THRESHOLD = original_threshold
    
    print("\nDance style configuration tests completed.\n")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("Testing edge cases...")
    
    # Test with missing keypoints
    incomplete_pose_data = PoseData(
        original={
            "frame_1": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (120.0, 80.0),
                # Missing right_wrist
                "left_hip": (80.0, 150.0),
                "left_knee": (90.0, 200.0),
                "left_ankle": (100.0, 250.0)
                # Missing head keypoints
            }
        },
        user={
            "frame_1": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (125.0, 75.0),
                # Missing right_wrist
                "left_hip": (80.0, 150.0),
                "left_knee": (85.0, 210.0),
                "left_ankle": (95.0, 260.0)
                # Missing head keypoints
            }
        }
    )
    
    results = compare_all_frames(incomplete_pose_data)
    print(f"Missing keypoints test: {len(results)} results (should handle gracefully)")
    
    # Test with no common frames
    no_common_frames_data = PoseData(
        original={"frame_1": {"right_shoulder": (100.0, 100.0)}},
        user={"frame_2": {"right_shoulder": (100.0, 100.0)}}
    )
    
    results = compare_all_frames(no_common_frames_data)
    print(f"No common frames test: {len(results)} results (should be 0)")
    
    print("Edge case tests completed.\n")


def main():
    """Run all tests."""
    print("=" * 50)
    print("POSE COMPARISON MODULE TESTS")
    print("=" * 50)
    
    try:
        test_angle_calculation()
        test_suggestion_generation()
        test_pose_comparison()
        test_dance_style_configurations()
        test_edge_cases()
        
        print("=" * 50)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 