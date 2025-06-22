"""
Data models for the dance analysis backend.

This module defines the data structures used for pose comparison and analysis.
"""

from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel


class PoseData(BaseModel):
    """
    Container for pose data from both original reference and user performance.
    
    Attributes:
        original: Dictionary mapping frame IDs to pose keypoints for reference performance
        user: Dictionary mapping frame IDs to pose keypoints for user performance
    """
    original: Dict[str, Dict[str, Tuple[float, float]]]
    user: Dict[str, Dict[str, Tuple[float, float]]]


class JointIssue(BaseModel):
    """
    Represents a specific joint angle difference between reference and user poses.
    
    Attributes:
        joint: Name of the joint (e.g., "right_arm", "left_leg", "head_tilt")
        delta_angle: Difference in degrees between reference and user angles
        suggestion: Human-readable suggestion for correction
    """
    joint: str
    delta_angle: float
    suggestion: str


class FrameComparisonResult(BaseModel):
    """
    Result of comparing poses for a specific frame.
    
    Attributes:
        frame_id: Identifier for the frame being compared
        total_error: Sum of all joint angle differences for this frame
        joint_issues: List of specific joint issues found in this frame
        suggestions: List of human-readable suggestions for improvement
        timestamp: Timestamp in seconds for this frame (calculated from FPS)
    """
    frame_id: str
    total_error: float
    joint_issues: List[JointIssue]
    suggestions: List[str]
    timestamp: Optional[float] = None 