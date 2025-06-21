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
        "torso": ["left_shoulder", "left_hip", "left_knee"],
        "torso_alt": ["right_shoulder", "right_hip", "right_knee"]
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
            "priority_joints": ["right_arm", "left_arm", "right_leg", "left_leg"],
            "description": "Great for beginners - only flags major differences"
        },
        "intermediate": {
            "name": "Intermediate (Balanced)",
            "angle_threshold": 10.0,  # Standard threshold
            "priority_joints": ["right_arm", "left_arm", "torso"],
            "description": "Balanced analysis for most dancers"
        },
        "advanced": {
            "name": "Advanced (Precise)",
            "angle_threshold": 6.0,  # Very strict
            "priority_joints": ["right_arm", "left_arm", "right_leg", "left_leg", "torso"],
            "description": "For advanced dancers - catches subtle differences"
        }
    }
    
    # Humanized suggestion templates
    SUGGESTION_TEMPLATES = {
        "right_arm": {
            "positive": [
                "Lower your right arm a bit more",
                "Bring your right arm down slightly",
                "Drop your right arm a little",
                "Let your right arm hang lower"
            ],
            "negative": [
                "Raise your right arm a bit more",
                "Lift your right arm slightly higher",
                "Bring your right arm up more",
                "Extend your right arm upward"
            ],
            "straighten": [
                "Straighten your right arm more",
                "Extend your right arm fully",
                "Unbend your right arm",
                "Make your right arm straighter"
            ],
            "bend": [
                "Bend your right arm more",
                "Flex your right arm",
                "Bend your elbow more",
                "Make your right arm more bent"
            ]
        },
        "left_arm": {
            "positive": [
                "Lower your left arm a bit more",
                "Bring your left arm down slightly",
                "Drop your left arm a little",
                "Let your left arm hang lower"
            ],
            "negative": [
                "Raise your left arm a bit more",
                "Lift your left arm slightly higher",
                "Bring your left arm up more",
                "Extend your left arm upward"
            ],
            "straighten": [
                "Straighten your left arm more",
                "Extend your left arm fully",
                "Unbend your left arm",
                "Make your left arm straighter"
            ],
            "bend": [
                "Bend your left arm more",
                "Flex your left arm",
                "Bend your elbow more",
                "Make your left arm more bent"
            ]
        },
        "right_leg": {
            "positive": [
                "Lower your right leg a bit more",
                "Bend your right knee slightly more",
                "Drop your right leg down more",
                "Sink into your right leg more"
            ],
            "negative": [
                "Raise your right leg a bit more",
                "Straighten your right leg more",
                "Lift your right leg higher",
                "Extend your right leg more"
            ]
        },
        "left_leg": {
            "positive": [
                "Lower your left leg a bit more",
                "Bend your left knee slightly more",
                "Drop your left leg down more",
                "Sink into your left leg more"
            ],
            "negative": [
                "Raise your left leg a bit more",
                "Straighten your left leg more",
                "Lift your left leg higher",
                "Extend your left leg more"
            ]
        },
        "torso": {
            "positive": [
                "Straighten your posture a bit more",
                "Stand up a little straighter",
                "Pull your shoulders back slightly",
                "Lengthen your spine more"
            ],
            "negative": [
                "Bend your torso a bit more",
                "Lean forward slightly more",
                "Relax your posture a little",
                "Let your upper body bend more"
            ]
        },
        "torso_alt": {
            "positive": [
                "Straighten your posture a bit more",
                "Stand up a little straighter",
                "Pull your shoulders back slightly",
                "Lengthen your spine more"
            ],
            "negative": [
                "Bend your torso a bit more",
                "Lean forward slightly more",
                "Relax your posture a little",
                "Let your upper body bend more"
            ]
        }
    }
    
    # Arm straightness thresholds
    STRAIGHT_THRESHOLD = 160.0  # Consider "straight" if > 160°
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
        import random
        
        templates = cls.SUGGESTION_TEMPLATES.get(joint, {})
        if not templates:
            return f"Adjust your {joint} slightly"
        
        if delta > 0:
            suggestions = templates.get("positive", [])
        else:
            suggestions = templates.get("negative", [])
        
        if suggestions:
            return random.choice(suggestions)
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