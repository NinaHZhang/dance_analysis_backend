#!/usr/bin/env python3
"""
Debug script to analyze torso vs knee angles in pose_output (1).json
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
    
    print("=== TORSO VS KNEE ANGLE ANALYSIS ===")
    print()
    
    # Torso configuration: left_shoulder -> left_hip -> left_knee
    torso_config = ["left_shoulder", "left_hip", "left_knee"]
    
    # Knee configuration: left_hip -> left_knee -> left_ankle
    knee_config = ["left_hip", "left_knee", "left_ankle"]
    
    # Calculate torso angles
    orig_shoulder = tuple(original_frame["left_shoulder"])
    orig_hip = tuple(original_frame["left_hip"])
    orig_knee = tuple(original_frame["left_knee"])
    orig_ankle = tuple(original_frame["left_ankle"])
    
    user_shoulder = tuple(user_frame["left_shoulder"])
    user_hip = tuple(user_frame["left_hip"])
    user_knee = tuple(user_frame["left_knee"])
    user_ankle = tuple(user_frame["left_ankle"])
    
    # Calculate angles
    orig_torso_angle = calculate_angle(orig_shoulder, orig_hip, orig_knee)
    user_torso_angle = calculate_angle(user_shoulder, user_hip, user_knee)
    
    orig_knee_angle = calculate_angle(orig_hip, orig_knee, orig_ankle)
    user_knee_angle = calculate_angle(user_hip, user_knee, user_ankle)
    
    print("=== ANGLE COMPARISONS ===")
    print(f"Torso angles:")
    print(f"  Original: {orig_torso_angle:.2f}°")
    print(f"  User: {user_torso_angle:.2f}°")
    print(f"  Difference: {user_torso_angle - orig_torso_angle:.2f}°")
    print()
    
    print(f"Knee angles:")
    print(f"  Original: {orig_knee_angle:.2f}°")
    print(f"  User: {user_knee_angle:.2f}°")
    print(f"  Difference: {user_knee_angle - orig_knee_angle:.2f}°")
    print()
    
    # Check thresholds
    torso_threshold = 10.0  # Advanced difficulty
    knee_threshold = 16.0   # Advanced difficulty leg threshold
    
    print("=== THRESHOLD ANALYSIS ===")
    torso_diff = abs(user_torso_angle - orig_torso_angle)
    knee_diff = abs(user_knee_angle - orig_knee_angle)
    
    print(f"Torso difference: {torso_diff:.2f}° (threshold: {torso_threshold}°)")
    print(f"  Would flag torso: {torso_diff > torso_threshold}")
    print()
    
    print(f"Knee difference: {knee_diff:.2f}° (threshold: {knee_threshold}°)")
    print(f"  Would flag knee: {knee_diff > knee_threshold}")
    print()
    
    # Show coordinate positions
    print("=== COORDINATE POSITIONS ===")
    print("Original pose:")
    print(f"  Shoulder: {orig_shoulder}")
    print(f"  Hip: {orig_hip}")
    print(f"  Knee: {orig_knee}")
    print(f"  Ankle: {orig_ankle}")
    print()
    
    print("User pose:")
    print(f"  Shoulder: {user_shoulder}")
    print(f"  Hip: {user_hip}")
    print(f"  Knee: {user_knee}")
    print(f"  Ankle: {user_ankle}")
    print()
    
    # Check if torso angle is actually detecting knee differences
    print("=== ANALYSIS ===")
    if torso_diff > torso_threshold and knee_diff > knee_threshold:
        print("Both torso and knee are being flagged - this might be correct")
    elif torso_diff > torso_threshold and knee_diff <= knee_threshold:
        print("Only torso is being flagged - might be detecting actual torso differences")
    elif torso_diff <= torso_threshold and knee_diff > knee_threshold:
        print("Only knee is being flagged - torso suggestion might be wrong")
    else:
        print("Neither is being flagged significantly")

if __name__ == "__main__":
    main() 