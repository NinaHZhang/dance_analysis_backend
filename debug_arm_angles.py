#!/usr/bin/env python3
"""
Debug script to analyze arm angles in pose_output (1).json
"""

import json
import math
from typing import Tuple

def calculate_angle(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
    """Calculate the angle between three points (p1 -> p2 -> p3)."""
    # Calculate vectors
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    
    # Calculate dot product
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    
    # Calculate magnitudes
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    # Avoid division by zero
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    # Calculate cosine of angle
    cos_angle = dot_product / (mag1 * mag2)
    
    # Clamp to valid range for acos
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    # Convert to degrees
    angle_rad = math.acos(cos_angle)
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg

def main():
    # Load the pose data
    with open('pose_output (1).json', 'r') as f:
        data = json.load(f)
    
    # Get frame_1 data
    original_frame = data['original']['frame_1']
    user_frame = data['user']['frame_1']
    
    # Left arm keypoints: left_shoulder -> left_elbow -> left_wrist
    left_arm_config = ["left_shoulder", "left_elbow", "left_wrist"]
    
    print("=== LEFT ARM ANGLE ANALYSIS ===")
    print()
    
    # Calculate original left arm angle
    orig_shoulder = tuple(original_frame["left_shoulder"])
    orig_elbow = tuple(original_frame["left_elbow"])
    orig_wrist = tuple(original_frame["left_wrist"])
    orig_angle = calculate_angle(orig_shoulder, orig_elbow, orig_wrist)
    
    # Calculate user left arm angle
    user_shoulder = tuple(user_frame["left_shoulder"])
    user_elbow = tuple(user_frame["left_elbow"])
    user_wrist = tuple(user_frame["left_wrist"])
    user_angle = calculate_angle(user_shoulder, user_elbow, user_wrist)
    
    print(f"Original left arm angle: {orig_angle:.2f}°")
    print(f"User left arm angle: {user_angle:.2f}°")
    print(f"Angle difference: {user_angle - orig_angle:.2f}°")
    print()
    
    # Check thresholds
    straight_threshold = 155.0
    bent_threshold = 140.0
    
    print("=== THRESHOLD ANALYSIS ===")
    print(f"Straight threshold: {straight_threshold}°")
    print(f"Bent threshold: {bent_threshold}°")
    print()
    
    print("Original arm:")
    print(f"  Is straight (> {straight_threshold}°): {orig_angle > straight_threshold}")
    print(f"  Is bent (< {bent_threshold}°): {orig_angle < bent_threshold}")
    print()
    
    print("User arm:")
    print(f"  Is straight (> {straight_threshold}°): {user_angle > straight_threshold}")
    print(f"  Is bent (< {bent_threshold}°): {user_angle < bent_threshold}")
    print()
    
    # Check difficulty thresholds
    difficulty_levels = {
        "beginner": {"angle_threshold": 15.0},
        "intermediate": {"angle_threshold": 10.0},
        "advanced": {"angle_threshold": 6.0}
    }
    
    print("=== DIFFICULTY THRESHOLD ANALYSIS ===")
    angle_diff = abs(user_angle - orig_angle)
    for difficulty, config in difficulty_levels.items():
        threshold = config["angle_threshold"]
        would_flag = angle_diff > threshold
        print(f"{difficulty.capitalize()}: threshold={threshold}°, difference={angle_diff:.2f}°, would_flag={would_flag}")
    
    print()
    
    # Show coordinate positions
    print("=== COORDINATE POSITIONS ===")
    print("Original left arm:")
    print(f"  Shoulder: {orig_shoulder}")
    print(f"  Elbow: {orig_elbow}")
    print(f"  Wrist: {orig_wrist}")
    print()
    
    print("User left arm:")
    print(f"  Shoulder: {user_shoulder}")
    print(f"  Elbow: {user_elbow}")
    print(f"  Wrist: {user_wrist}")

if __name__ == "__main__":
    main() 