"""
Configuration settings for the dance analysis backend.

This module centralizes all configurable parameters for easy adjustment
and maintenance.
"""

from typing import Dict, List


class DanceAnalysisConfig:
    """Configuration class for dance analysis parameters."""
    
    # Angle calculation settings
    ANGLE_THRESHOLD = 10.0  # Minimum angle difference to report (degrees)
    TOP_N_FRAMES = 3       # Number of top problematic frames to return
    
    # Joint configurations for analysis
    JOINT_CONFIGS = {
        "right_arm": ["right_shoulder", "right_elbow", "right_wrist"],
        "left_arm": ["left_shoulder", "left_elbow", "left_wrist"],
        "right_leg": ["right_hip", "right_knee", "right_ankle"],
        "left_leg": ["left_hip", "left_knee", "left_ankle"],
        "right_knee": ["right_hip", "right_knee", "right_ankle"],  # Knee-specific analysis
        "left_knee": ["left_hip", "left_knee", "left_ankle"],      # Knee-specific analysis
        "torso": ["left_shoulder", "left_hip", "left_knee"]
    }
    
    # Keypoint definitions
    KEYPOINTS = {
        "left_shoulder": "left_shoulder",
        "right_shoulder": "right_shoulder",
        "left_elbow": "left_elbow",
        "right_elbow": "right_elbow",
        "left_wrist": "left_wrist",
        "right_wrist": "right_wrist",
        "left_hip": "left_hip",
        "right_hip": "right_hip",
        "left_knee": "left_knee",
        "right_knee": "right_knee",
        "left_ankle": "left_ankle",
        "right_ankle": "right_ankle"
    }
    
    # Difficulty level configurations
    DIFFICULTY_LEVELS = {
        "beginner": {
            "name": "Beginner (More Forgiving)",
            "angle_threshold": 15.0,  # Very lenient
            "leg_angle_threshold": 30.0,  # Higher threshold for legs to reduce false positives
            "torso_angle_threshold": 20.0,  # New, increased for torso
            "priority_joints": ["right_arm", "left_arm", "right_knee", "left_knee"],
            "description": "Great for beginners - only flags major differences"
        },
        "intermediate": {
            "name": "Intermediate (Balanced)",
            "angle_threshold": 10.0,  # Standard threshold
            "leg_angle_threshold": 18.0,  # Higher threshold for legs
            "priority_joints": ["right_arm", "left_arm", "right_knee", "left_knee"],
            "description": "Balanced analysis for most dancers"
        },
        "advanced": {
            "name": "Advanced (Precise)",
            "angle_threshold": 6.0,  # Very strict
            "leg_angle_threshold": 16.0,  # Higher threshold for legs but still precise
            "torso_angle_threshold": 10.0,  # New, increased for torso
            "priority_joints": ["right_arm", "left_arm", "right_knee", "left_knee", "torso"],
            "description": "For advanced dancers - catches subtle differences"
        }
    }
    
    # Humanized suggestion templates
    SUGGESTION_TEMPLATES = {
        "right_arm": {
            "positive": [
                "Lower your right arm a bit more"
            ],
            "negative": [
                "Raise your right arm a bit more"
            ],
            "straighten": [
                "Straighten your right arm more"
            ],
            "bend": [
                "Bend your right arm more"
            ]
        },
        "left_arm": {
            "positive": [
                "Lower your left arm a bit more"
            ],
            "negative": [
                "Raise your left arm a bit more"
            ],
            "straighten": [
                "Straighten your left arm more"
            ],
            "bend": [
                "Bend your left arm more"
            ]
        },
        "right_leg": {
            "positive": [
                "Adjust your right leg position"
            ],
            "negative": [
                "Adjust your right leg position"
            ]
        },
        "left_leg": {
            "positive": [
                "Adjust your left leg position"
            ],
            "negative": [
                "Adjust your left leg position"
            ]
        },
        "right_knee": {
            "positive": [
                "Bend your knees more"
            ],
            "negative": [
                "Straighten your knees more"
            ],
            "straighten": [
                "Straighten your knees more"
            ],
            "bend": [
                "Bend your knees more"
            ]
        },
        "left_knee": {
            "positive": [
                "Bend your knees more"
            ],
            "negative": [
                "Straighten your knees more"
            ],
            "straighten": [
                "Straighten your knees more"
            ],
            "bend": [
                "Bend your knees more"
            ]
        },
        "torso": {
            "positive": [
                "Straighten your posture a bit more"
            ],
            "negative": [
                "Bend your torso a bit more"
            ]
        },
        "torso_alt": {
            "positive": [
                "Straighten your posture a bit more"
            ],
            "negative": [
                "Bend your torso a bit more"
            ]
        }
    }
    
    # Arm straightness thresholds
    STRAIGHT_THRESHOLD = 155.0  # Consider "straight" if > 155° (lowered from 160°)
    BENT_THRESHOLD = 140.0      # Consider "bent" if < 140°
    PERFECT_STRAIGHT = 180.0    # Perfectly straight arm
    
    @classmethod
    def get_difficulty_config(cls, difficulty: str) -> Dict:
        """Get configuration for a specific difficulty level."""
        return cls.DIFFICULTY_LEVELS.get(difficulty, {
            "name": "Intermediate (Balanced)",
            "angle_threshold": cls.ANGLE_THRESHOLD,
            "priority_joints": list(cls.JOINT_CONFIGS.keys()),
            "description": "Balanced analysis for most dancers"
        })
    
    @classmethod
    def get_humanized_suggestion(cls, joint: str, delta: float) -> str:
        """Generate a humanized suggestion for a joint difference."""
        templates = cls.SUGGESTION_TEMPLATES.get(joint, {})
        if not templates:
            return f"Adjust your {joint} slightly"
        
        if delta > 0:
            suggestions = templates.get("positive", [])
        else:
            suggestions = templates.get("negative", [])
        
        if suggestions:
            return suggestions[0]
        else:
            return f"Adjust your {joint} slightly"
    
    @classmethod
    def update_threshold(cls, new_threshold: float):
        """Update the global angle threshold."""
        cls.ANGLE_THRESHOLD = new_threshold
    
    @classmethod
    def update_top_n_frames(cls, new_top_n: int):
        """Update the number of top frames to return."""
        cls.TOP_N_FRAMES = new_top_n


# Global configuration instance
config = DanceAnalysisConfig() 