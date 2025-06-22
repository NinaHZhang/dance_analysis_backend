#!/usr/bin/env python3
"""
Debug script to analyze angle differences across all frames and difficulty levels.
"""

import json
import os
from compare import compare_frame_poses, calculate_joint_angle, JOINT_CONFIGS
from models import PoseData
from config import config
from process_real_data import parse_json_pose_data, detect_file_format

def debug_left_arm_analysis(file_path: str):
    """Debug left arm analysis specifically."""
    print(f"🔍 DEBUGGING LEFT ARM ANALYSIS")
    print(f"File: {file_path}")
    print("=" * 80)
    
    # Parse the file
    file_format = detect_file_format(file_path)
    pose_data = parse_json_pose_data(file_path)
    
    print(f"📊 Parsed {len(pose_data.original)} original frames and {len(pose_data.user)} user frames")
    
    # Get common frames
    common_frames = set(pose_data.original.keys()) & set(pose_data.user.keys())
    print(f"🔄 Common frames: {len(common_frames)}")
    
    # Analyze first few frames for left arm specifically
    for frame_id in sorted(common_frames)[:5]:
        print(f"\n📷 FRAME: {frame_id}")
        print("-" * 40)
        
        original_pose = pose_data.original[frame_id]
        user_pose = pose_data.user[frame_id]
        
        # Calculate left arm angle specifically
        left_arm_keypoints = JOINT_CONFIGS["left_arm"]
        original_angle = calculate_joint_angle(original_pose, left_arm_keypoints)
        user_angle = calculate_joint_angle(user_pose, left_arm_keypoints)
        
        if original_angle is not None and user_angle is not None:
            delta_angle = user_angle - original_angle
            
            print(f"Left Arm Analysis:")
            print(f"  Original angle: {original_angle:.1f}°")
            print(f"  User angle: {user_angle:.1f}°")
            print(f"  Delta: {delta_angle:.1f}°")
            
            # Check straightness
            straight_threshold = config.STRAIGHT_THRESHOLD
            bent_threshold = config.BENT_THRESHOLD
            
            print(f"\nStraightness Analysis:")
            print(f"  Original is straight (>160°): {original_angle > straight_threshold}")
            print(f"  User is straight (>160°): {user_angle > straight_threshold}")
            print(f"  Original is bent (<140°): {original_angle < bent_threshold}")
            print(f"  User is bent (<140°): {user_angle < bent_threshold}")
            
            # Show coordinates
            print(f"\nCoordinates:")
            print(f"  Original left_shoulder: {original_pose['left_shoulder']}")
            print(f"  Original left_elbow: {original_pose['left_elbow']}")
            print(f"  Original left_wrist: {original_pose['left_wrist']}")
            print(f"  User left_shoulder: {user_pose['left_shoulder']}")
            print(f"  User left_elbow: {user_pose['left_elbow']}")
            print(f"  User left_wrist: {user_pose['left_wrist']}")
            
            # Test the suggestion generation
            print(f"\nSuggestion Test:")
            from compare import _generate_humanized_suggestion_with_straighten_bend
            suggestion = _generate_humanized_suggestion_with_straighten_bend(
                "left_arm", original_angle, user_angle, delta_angle, "intermediate"
            )
            print(f"  Generated suggestion: {suggestion}")

def main():
    """Main function."""
    # Look for pose data files
    pose_files = []
    for file in os.listdir('.'):
        if file.endswith('.json'):
            file_lower = file.lower()
            if any(keyword in file_lower for keyword in ['pose', 'dance', 'arm', 'nin', 'vertopal']):
                pose_files.append(file)
    
    if not pose_files:
        print("No pose data files found!")
        return
    
    # Process the pose_output (17).json file specifically
    target_file = "pose_output (17).json"
    if target_file in pose_files:
        debug_left_arm_analysis(target_file)
    else:
        print(f"File {target_file} not found!")

if __name__ == "__main__":
    main() 