"""
Pose Comparison and Keyframe Selector Module.

This module provides functionality to compare dance poses between reference and user performances,
calculate joint angle differences, and select the most problematic keyframes for analysis.

Main Functions:
    - compare_all_frames: Main function that processes pose data and returns comparison results
    - calculate_angle: Helper function to calculate angle between three points
    - generate_suggestion: Helper function to generate human-readable suggestions

Joint Definitions:
    - right_arm: Shoulder -> Elbow -> Wrist
    - left_arm: Shoulder -> Elbow -> Wrist
    - right_leg: Hip -> Knee -> Ankle  
    - left_leg: Hip -> Knee -> Ankle
    - head_tilt: Ear -> Eye -> Shoulder (for head orientation)
    - torso: Shoulder -> Hip -> Knee (for body alignment)
"""

import math
from typing import Dict, List, Tuple, Optional
from models import PoseData, FrameComparisonResult, JointIssue
from config import config


# Use configuration from config module
KEYPOINTS = config.KEYPOINTS
JOINT_CONFIGS = config.JOINT_CONFIGS
ANGLE_THRESHOLD = config.ANGLE_THRESHOLD
TOP_N_FRAMES = config.TOP_N_FRAMES


def calculate_angle(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
    """
    Calculate the angle between three points (p1 -> p2 -> p3).
    
    Args:
        p1: First point as (x, y) tuple
        p2: Middle point (vertex) as (x, y) tuple  
        p3: Third point as (x, y) tuple
        
    Returns:
        Angle in degrees between the three points
        
    Raises:
        ValueError: If any point is None or invalid
    """
    if not all(p1) and not all(p2) and not all(p3):
        raise ValueError("All points must be valid (x, y) coordinates")
    
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


def calculate_joint_angle(pose: Dict[str, Tuple[float, float]], joint_config: List[str]) -> Optional[float]:
    """
    Calculate the angle for a specific joint configuration.
    
    Args:
        pose: Dictionary mapping keypoint names to (x, y) coordinates
        joint_config: List of three keypoint names defining the joint
        
    Returns:
        Angle in degrees, or None if any required keypoint is missing
    """
    try:
        points = []
        for keypoint in joint_config:
            if keypoint not in pose:
                return None
            points.append(pose[keypoint])
        
        return calculate_angle(points[0], points[1], points[2])
    except (ValueError, KeyError):
        return None


def generate_suggestion(joint: str, delta: float) -> str:
    """
    Generate a human-readable suggestion for correcting a joint angle difference.
    
    Args:
        joint: Name of the joint (e.g., "right_arm", "left_leg", "torso")
        delta: Angle difference in degrees (positive means user angle is larger)
        
    Returns:
        Human-readable suggestion string
    """
    # Use humanized suggestions from config
    return config.get_humanized_suggestion(joint, delta)


def compare_frame_poses(original_pose: Dict[str, Tuple[float, float]], 
                       user_pose: Dict[str, Tuple[float, float]], 
                       frame_id: str) -> Optional[FrameComparisonResult]:
    """
    Compare poses for a single frame and calculate joint differences.
    
    Args:
        original_pose: Reference pose keypoints
        user_pose: User pose keypoints
        frame_id: Identifier for the frame
        
    Returns:
        FrameComparisonResult if valid comparison can be made, None otherwise
    """
    joint_issues = []
    total_error = 0.0
    
    # Calculate angles for each joint configuration
    for joint_name, keypoints in JOINT_CONFIGS.items():
        original_angle = calculate_joint_angle(original_pose, keypoints)
        user_angle = calculate_joint_angle(user_pose, keypoints)
        
        # Skip if we can't calculate either angle
        if original_angle is None or user_angle is None:
            continue
        
        # Calculate angle difference
        delta_angle = user_angle - original_angle
        
        # Only include if difference exceeds threshold
        if abs(delta_angle) > ANGLE_THRESHOLD:
            suggestion = generate_suggestion(joint_name, delta_angle)
            joint_issue = JointIssue(
                joint=joint_name,
                delta_angle=delta_angle,
                suggestion=suggestion
            )
            joint_issues.append(joint_issue)
            total_error += abs(delta_angle)
    
    # Only return result if there are significant issues
    if joint_issues:
        suggestions = [issue.suggestion for issue in joint_issues]
        return FrameComparisonResult(
            frame_id=frame_id,
            total_error=total_error,
            joint_issues=joint_issues,
            suggestions=suggestions
        )
    
    return None


def compare_all_frames(pose_data: PoseData) -> List[FrameComparisonResult]:
    """
    Compare all frames between reference and user poses, selecting the top N problematic frames.
    
    This is the main function that:
    1. Compares each frame between reference and user poses
    2. Calculates joint angle differences for arms, legs, and head
    3. Identifies frames with significant pose errors (>10° threshold)
    4. Ranks frames by total error and returns top 3
    
    Args:
        pose_data: PoseData object containing original and user pose dictionaries
        
    Returns:
        List of FrameComparisonResult objects for the top N problematic frames,
        sorted by total error (highest first)
        
    Example:
        >>> pose_data = PoseData(
        ...     original={"frame_1": {"right_shoulder": (100, 100), ...}},
        ...     user={"frame_1": {"right_shoulder": (105, 95), ...}}
        ... )
        >>> results = compare_all_frames(pose_data)
        >>> print(f"Found {len(results)} problematic frames")
    """
    frame_results = []
    
    # Get common frames between original and user data
    common_frames = set(pose_data.original.keys()) & set(pose_data.user.keys())
    
    if not common_frames:
        return []
    
    # Compare each frame
    for frame_id in common_frames:
        original_pose = pose_data.original[frame_id]
        user_pose = pose_data.user[frame_id]
        
        result = compare_frame_poses(original_pose, user_pose, frame_id)
        if result:
            frame_results.append(result)
    
    # Sort by total error (highest first) and return top N
    frame_results.sort(key=lambda x: x.total_error, reverse=True)
    
    return frame_results[:TOP_N_FRAMES]


# Example usage and testing functions
def validate_pose_data(pose_data: PoseData) -> bool:
    """
    Validate that pose data contains required keypoints for analysis.
    
    Args:
        pose_data: PoseData object to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    required_keypoints = set()
    for keypoints in JOINT_CONFIGS.values():
        required_keypoints.update(keypoints)
    
    # Check if at least one frame has required keypoints
    for frame_poses in [pose_data.original, pose_data.user]:
        for pose in frame_poses.values():
            if all(keypoint in pose for keypoint in required_keypoints):
                return True
    
    return False


def get_analysis_summary(results: List[FrameComparisonResult]) -> Dict:
    """
    Generate a summary of the analysis results.
    
    Args:
        results: List of FrameComparisonResult objects
        
    Returns:
        Dictionary with summary statistics
    """
    if not results:
        return {"total_frames_analyzed": 0, "problematic_frames": 0}
    
    total_error = sum(r.total_error for r in results)
    avg_error = total_error / len(results)
    
    joint_counts = {}
    for result in results:
        for issue in result.joint_issues:
            joint_counts[issue.joint] = joint_counts.get(issue.joint, 0) + 1
    
    return {
        "total_frames_analyzed": len(results),
        "total_error": total_error,
        "average_error": avg_error,
        "most_problematic_joint": max(joint_counts.items(), key=lambda x: x[1])[0] if joint_counts else None,
        "joint_issue_counts": joint_counts
    } 