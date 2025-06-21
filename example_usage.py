"""
Comprehensive example demonstrating the dance analysis backend features.

This script shows how to use all the new features including:
- Dance style configurations
- Expanded joint analysis
- API endpoints
- Configuration management
"""

import json
from models import PoseData
from compare import compare_all_frames, get_analysis_summary
from config import config


def create_sample_dance_data():
    """Create realistic sample dance pose data."""
    return PoseData(
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
                "left_knee": (85.0, 210.0),    # 6° difference
                "left_ankle": (95.0, 260.0),   # 6° difference
                "left_ear": (90.0, 85.0),      # 5° difference
                "left_eye": (95.0, 80.0),      # 5° difference
                "right_ear": (110.0, 85.0),    # 5° difference
                "right_eye": (105.0, 80.0)     # 5° difference
            },
            "frame_2": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (115.0, 85.0),  # 5° difference
                "right_wrist": (125.0, 75.0),  # 5° difference
                "left_shoulder": (80.0, 100.0),
                "left_elbow": (65.0, 85.0),    # 5° difference
                "left_wrist": (55.0, 75.0),    # 5° difference
                "right_hip": (100.0, 150.0),
                "right_knee": (100.0, 215.0),  # 5° difference
                "right_ankle": (105.0, 265.0), # 5° difference
                "left_hip": (80.0, 150.0),
                "left_knee": (80.0, 215.0),    # 5° difference
                "left_ankle": (85.0, 265.0),   # 5° difference
                "left_ear": (95.0, 90.0),
                "left_eye": (100.0, 85.0),
                "right_ear": (105.0, 90.0),
                "right_eye": (100.0, 85.0)
            }
        }
    )


def demonstrate_dance_style_analysis():
    """Demonstrate analysis with different dance styles."""
    print("=" * 60)
    print("DANCE STYLE ANALYSIS DEMONSTRATION")
    print("=" * 60)
    
    pose_data = create_sample_dance_data()
    
    for style in ["ballet", "contemporary", "hip_hop"]:
        print(f"\n{style.upper()} STYLE ANALYSIS:")
        print("-" * 40)
        
        # Get style configuration
        style_config = config.get_style_config(style)
        print(f"Threshold: {style_config['angle_threshold']}°")
        print(f"Priority joints: {style_config['priority_joints']}")
        
        # Temporarily update configuration
        original_threshold = config.ANGLE_THRESHOLD
        config.update_threshold(style_config['angle_threshold'])
        
        # Update compare module
        import compare
        compare.ANGLE_THRESHOLD = style_config['angle_threshold']
        
        # Run analysis
        results = compare_all_frames(pose_data)
        summary = get_analysis_summary(results)
        
        print(f"Results: {len(results)} problematic frames found")
        if results:
            for i, result in enumerate(results, 1):
                print(f"  Frame {i}: {result.frame_id}")
                print(f"    Total Error: {result.total_error:.2f}°")
                print(f"    Joint Issues: {len(result.joint_issues)}")
                for issue in result.joint_issues:
                    print(f"      - {issue.joint}: {issue.delta_angle:+.1f}°")
                print(f"    Suggestions:")
                for suggestion in result.suggestions:
                    print(f"      - {suggestion}")
        else:
            print("  No significant issues found for this dance style.")
        
        # Restore configuration
        config.update_threshold(original_threshold)
        compare.ANGLE_THRESHOLD = original_threshold


def demonstrate_joint_analysis():
    """Demonstrate the expanded joint analysis capabilities."""
    print("\n" + "=" * 60)
    print("EXPANDED JOINT ANALYSIS DEMONSTRATION")
    print("=" * 60)
    
    print(f"Available joint configurations: {list(config.JOINT_CONFIGS.keys())}")
    print(f"Total joints analyzed: {len(config.JOINT_CONFIGS)}")
    
    print("\nJoint definitions:")
    for joint, keypoints in config.JOINT_CONFIGS.items():
        print(f"  {joint}: {' → '.join(keypoints)}")
    
    # Test with contemporary style (standard threshold)
    pose_data = create_sample_dance_data()
    results = compare_all_frames(pose_data)
    
    print(f"\nAnalysis results with contemporary style (10° threshold):")
    print(f"Found {len(results)} problematic frames")
    
    if results:
        for result in results:
            print(f"\nFrame: {result.frame_id}")
            print(f"Total Error: {result.total_error:.2f}°")
            for issue in result.joint_issues:
                print(f"  {issue.joint}: {issue.delta_angle:+.1f}° - {issue.suggestion}")


def demonstrate_api_usage():
    """Demonstrate how to use the API endpoints."""
    print("\n" + "=" * 60)
    print("API USAGE DEMONSTRATION")
    print("=" * 60)
    
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /dance-styles - Get available dance styles")
    print("  POST /compare-poses - Compare poses with dance style")
    print("  POST /test-comparison - Test with sample data")
    
    print("\nExample API calls:")
    print("1. Get dance styles:")
    print("   curl -X GET http://localhost:8000/dance-styles")
    
    print("\n2. Compare poses with ballet style:")
    print("   curl -X POST http://localhost:8000/compare-poses \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"pose_data\": {...}, \"dance_style\": \"ballet\"}'")
    
    print("\n3. Health check:")
    print("   curl -X GET http://localhost:8000/health")


def demonstrate_configuration_management():
    """Demonstrate configuration management features."""
    print("\n" + "=" * 60)
    print("CONFIGURATION MANAGEMENT DEMONSTRATION")
    print("=" * 60)
    
    print("Current configuration:")
    print(f"  Default angle threshold: {config.ANGLE_THRESHOLD}°")
    print(f"  Top N frames: {config.TOP_N_FRAMES}")
    print(f"  Available dance styles: {list(config.DANCE_STYLES.keys())}")
    
    print("\nDance style configurations:")
    for style, style_config in config.DANCE_STYLES.items():
        print(f"  {style}:")
        print(f"    Threshold: {style_config['angle_threshold']}°")
        print(f"    Priority joints: {style_config['priority_joints']}")
    
    print("\nConfiguration update example:")
    print("  config.update_threshold(5.0)  # Make analysis more sensitive")
    print("  config.update_top_n_frames(5)  # Return top 5 frames")


def main():
    """Run all demonstrations."""
    print("DANCE ANALYSIS BACKEND - COMPREHENSIVE DEMONSTRATION")
    print("=" * 80)
    
    try:
        demonstrate_dance_style_analysis()
        demonstrate_joint_analysis()
        demonstrate_api_usage()
        demonstrate_configuration_management()
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"Demonstration failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 