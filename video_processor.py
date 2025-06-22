"""
Video processing module for dance analysis.

This module provides functionality to extract pose keypoints from videos
and convert them to the format expected by the dance analysis system.
"""

import mediapipe as mp
import cv2
import json
import numpy as np
import tempfile
import os
from typing import Dict, Tuple, Optional
from models import PoseData

# MediaPipe pose keypoint mapping to our system
KEYPOINT_MAPPING = {
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28
}

def extract_pose_from_video(video_path: str, output_path: Optional[str] = None) -> Dict:
    """
    Extract pose keypoints from a video using MediaPipe.
    
    Args:
        video_path: Path to the input video file
        output_path: Optional path to save the JSON output
        
    Returns:
        Dictionary containing frame-by-frame pose data
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(video_path)
    frames_data = {}
    frame_count = 0
    
    print(f"Processing video: {video_path}")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        if results.pose_landmarks:
            frame_data = {}
            landmarks = results.pose_landmarks.landmark
            
            # Extract only the keypoints we need
            for keypoint_name, landmark_id in KEYPOINT_MAPPING.items():
                if landmark_id < len(landmarks):
                    landmark = landmarks[landmark_id]
                    # Normalize coordinates (0-1) and ensure they're valid
                    if landmark.visibility > 0.5:  # Only use visible landmarks
                        frame_data[keypoint_name] = [landmark.x, landmark.y]
            
            # Only add frame if we have enough keypoints
            if len(frame_data) >= 8:  # At least 8 keypoints for basic analysis
                frames_data[f"frame_{frame_count}"] = frame_data
        
        frame_count += 1
        
        # Progress indicator
        if frame_count % 30 == 0:
            print(f"Processed {frame_count} frames...")
    
    cap.release()
    pose.close()
    
    print(f"Extracted pose data from {len(frames_data)} frames")
    
    # Save to JSON if output path provided
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(frames_data, f, indent=2)
        print(f"Saved pose data to: {output_path}")
    
    return frames_data

def process_video_comparison(
    original_video_path: str, 
    user_video_path: str, 
    difficulty: str = "intermediate",
    fps: float = 30.0
) -> Dict:
    """
    Complete pipeline: extract pose data from two videos and compare them.
    
    Args:
        original_video_path: Path to reference video
        user_video_path: Path to user performance video
        difficulty: Difficulty level for analysis
        fps: Frame rate for timestamp calculation
        
    Returns:
        Analysis results dictionary
    """
    try:
        # Create temporary files for pose data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            original_json_path = f.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            user_json_path = f.name
        
        # Extract pose data from both videos
        print("Extracting pose data from original video...")
        original_data = extract_pose_from_video(original_video_path, original_json_path)
        
        print("Extracting pose data from user video...")
        user_data = extract_pose_from_video(user_video_path, user_json_path)
        
        # Create PoseData object
        pose_data = PoseData(original=original_data, user=user_data)
        
        # Import analysis functions
        from compare import compare_all_frames, validate_pose_data, get_analysis_summary
        from config import config
        
        # Validate pose data
        if not validate_pose_data(pose_data):
            raise ValueError("Invalid pose data: missing required keypoints for analysis")
        
        # Get difficulty configuration
        difficulty_config = config.get_difficulty_config(difficulty)
        
        # Perform analysis
        results = compare_all_frames(pose_data, difficulty)
        
        # Add timestamps
        from process_real_data import calculate_timestamp
        for result in results:
            result.timestamp = calculate_timestamp(result.frame_id, fps)
        
        # Generate summary
        summary = get_analysis_summary(results)
        
        # Clean up temporary files
        os.unlink(original_json_path)
        os.unlink(user_json_path)
        
        return {
            "difficulty": difficulty,
            "difficulty_name": difficulty_config['name'],
            "threshold": difficulty_config['angle_threshold'],
            "fps": fps,
            "original_frames": len(original_data),
            "user_frames": len(user_data),
            "results": results,
            "summary": summary
        }
        
    except Exception as e:
        # Clean up temporary files on error
        try:
            if 'original_json_path' in locals():
                os.unlink(original_json_path)
            if 'user_json_path' in locals():
                os.unlink(user_json_path)
        except:
            pass
        raise e

def validate_video_file(video_path: str) -> bool:
    """
    Validate that a video file can be opened and processed.
    
    Args:
        video_path: Path to video file
        
    Returns:
        True if video is valid, False otherwise
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        
        # Try to read first frame
        ret, frame = cap.read()
        cap.release()
        
        return ret and frame is not None
    except:
        return False 