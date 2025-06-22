#!/usr/bin/env python3
"""
Local video processing tool for dance analysis.

This module integrates MediaPipe pose extraction with the dance analysis system,
converting videos directly to coordinate JSON files that can be analyzed.
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import os
import argparse
from typing import Dict, List, Optional
from models import PoseData
from compare import compare_all_frames, validate_pose_data, get_analysis_summary
from config import config
from process_real_data import calculate_timestamp

# Only the joints you care about
DESIRED = [
    "RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST",
    "LEFT_SHOULDER",  "LEFT_ELBOW",  "LEFT_WRIST",
    "RIGHT_HIP",      "RIGHT_KNEE",  "RIGHT_ANKLE",
    "LEFT_HIP",       "LEFT_KNEE",   "LEFT_ANKLE",
]

def process_video_to_json(path: str, sample_fps: float = 1.0) -> dict:
    """
    Reads the video at `path`, runs MediaPipe Pose on it,
    samples at t=0, t=1/sample_fps, t=2/sample_fps, ...,
    and returns a dict mapping "frame_1", "frame_2", ... to
    { joint_name: [x_norm, y_norm], ... } for DESIRED joints,
    with coords flipped so (0,0)=bottom-left, (1,1)=top-right.
    """
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {path}")

    src_fps = cap.get(cv2.CAP_PROP_FPS) or sample_fps
    step    = max(int(round(src_fps / sample_fps)), 1)

    mp_pose     = mp.solutions.pose
    data        = {}
    frame_idx   = 1
    frame_count = 0

    print(f"Processing video: {path}")
    print(f"Source FPS: {src_fps}, Sample FPS: {sample_fps}, Step: {step}")

    with mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            # sample first frame or every `step`th frame
            if not (frame_count == 1 or frame_count % step == 0):
                continue

            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            key    = f"frame_{frame_idx}"
            coords = {}
            if results.pose_landmarks:
                # extract desired joints
                for name in DESIRED:
                    lm = results.pose_landmarks.landmark[
                        mp_pose.PoseLandmark[name].value
                    ]
                    # flip both axes: x' = 1-x, y' = 1-y
                    x_norm = 1.0 - lm.x
                    y_norm = 1.0 - lm.y
                    coords[name.lower()] = [x_norm, y_norm]

            data[key] = coords
            frame_idx += 1
            
            # Progress indicator
            if frame_idx % 10 == 0:
                print(f"Processed {frame_idx} frames...")

    cap.release()
    print(f"Extracted pose data from {len(data)} frames")
    return data


def analyze_video_comparison(
    original_video: str,
    user_video: str,
    difficulty: str = "intermediate",
    sample_fps: float = 2.0,
    output_dir: str = "output"
) -> Dict:
    """
    Complete pipeline: process two videos and analyze dance performance.
    
    Args:
        original_video: Path to reference video
        user_video: Path to user performance video
        difficulty: Difficulty level (beginner, intermediate, advanced)
        sample_fps: Frame rate to sample from videos
        output_dir: Directory to save JSON files and results
        
    Returns:
        Analysis results dictionary
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Process both videos
        print("=" * 60)
        print("PROCESSING VIDEOS")
        print("=" * 60)
        
        original_data = process_video_to_json(original_video, sample_fps)
        user_data = process_video_to_json(user_video, sample_fps)
        
        # Save coordinate data
        original_json_path = os.path.join(output_dir, "original_coordinates.json")
        user_json_path = os.path.join(output_dir, "user_coordinates.json")
        
        with open(original_json_path, 'w') as f:
            json.dump(original_data, f, indent=2)
        with open(user_json_path, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        print(f"Saved coordinate data to:")
        print(f"  Original: {original_json_path}")
        print(f"  User: {user_json_path}")
        
        # Create PoseData object
        pose_data = PoseData(original=original_data, user=user_data)
        
        # Validate pose data
        if not validate_pose_data(pose_data):
            raise ValueError("Invalid pose data: missing required keypoints for analysis")
        
        # Get difficulty configuration
        difficulty_config = config.get_difficulty_config(difficulty)
        
        print("\n" + "=" * 60)
        print("DANCE ANALYSIS")
        print("=" * 60)
        print(f"Difficulty: {difficulty_config['name']}")
        print(f"Threshold: {difficulty_config['angle_threshold']}°")
        print(f"Sample FPS: {sample_fps}")
        print(f"Original frames: {len(original_data)}")
        print(f"User frames: {len(user_data)}")
        
        # Perform analysis
        results = compare_all_frames(pose_data, difficulty)
        
        # Add timestamps
        for result in results:
            result.timestamp = calculate_timestamp(result.frame_id, sample_fps)
        
        # Generate summary
        summary = get_analysis_summary(results)
        
        # Save analysis results
        results_json_path = os.path.join(output_dir, "analysis_results.json")
        
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            serializable_result = {
                "frame_id": result.frame_id,
                "timestamp": result.timestamp,
                "total_error": result.total_error,
                "suggestions": result.suggestions,
                "joint_issues": [
                    {
                        "joint": issue.joint,
                        "delta_angle": issue.delta_angle,
                        "suggestion": issue.suggestion
                    }
                    for issue in result.joint_issues
                ]
            }
            serializable_results.append(serializable_result)
        
        analysis_output = {
            "difficulty": difficulty,
            "difficulty_name": difficulty_config['name'],
            "threshold": difficulty_config['angle_threshold'],
            "sample_fps": sample_fps,
            "original_frames": len(original_data),
            "user_frames": len(user_data),
            "results": serializable_results,
            "summary": summary
        }
        
        with open(results_json_path, 'w') as f:
            json.dump(analysis_output, f, indent=2)
        
        print(f"\nAnalysis results saved to: {results_json_path}")
        
        return analysis_output
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise e


def view_two_videos_with_pose(
    orig_path: str,
    user_path: str,
    playback_speed: float = 1.0,
    window_name: str = "Side-by-Side Pose Comparison"
) -> None:
    """
    Opens two videos side-by-side in a single window with MediaPipe Pose overlay.
    `playback_speed` scales playback: 0.25 for quarter speed, 1.0 normal, 2.0 double.
    Press 'q' to exit.
    """
    cap1 = cv2.VideoCapture(orig_path)
    cap2 = cv2.VideoCapture(user_path)
    if not cap1.isOpened() or not cap2.isOpened():
        raise RuntimeError(f"Could not open videos: {orig_path}, {user_path}")

    # determine source FPS and compute delay per frame
    fps1 = cap1.get(cv2.CAP_PROP_FPS) or 30.0
    fps2 = cap2.get(cv2.CAP_PROP_FPS) or fps1
    fps  = min(fps1, fps2)
    delay_ms = int(1000 / (fps * playback_speed))

    mp_pose    = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    with mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        while True:
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()
            if not ret1 and not ret2:
                break

            # blank frames if one ends early
            if not ret1 and ret2:
                frame1 = np.zeros_like(frame2)
            if not ret2 and ret1:
                frame2 = np.zeros_like(frame1)
            if not (ret1 or ret2):
                break

            # process frame1
            if ret1:
                rgb1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                res1 = pose.process(rgb1)
                if res1.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        frame1, res1.pose_landmarks, mp_pose.POSE_CONNECTIONS
                    )

            # process frame2
            if ret2:
                rgb2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                res2 = pose.process(rgb2)
                if res2.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        frame2, res2.pose_landmarks, mp_pose.POSE_CONNECTIONS
                    )

            # stitch side by side
            combined_frame = np.hstack((frame1, frame2))
            cv2.imshow(window_name, combined_frame)

            if cv2.waitKey(delay_ms) & 0xFF == ord('q'):
                break

    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Dance Analysis Video Processor")
    parser.add_argument("original_video", help="Path to reference video")
    parser.add_argument("user_video", help="Path to user performance video")
    parser.add_argument("--difficulty", choices=["beginner", "intermediate", "advanced"], 
                       default="intermediate", help="Difficulty level")
    parser.add_argument("--sample-fps", type=float, default=2.0, 
                       help="Frame rate to sample from videos (default: 2.0)")
    parser.add_argument("--output-dir", default="output", 
                       help="Output directory for results (default: output)")
    parser.add_argument("--view", action="store_true", 
                       help="Open side-by-side video comparison after analysis")
    parser.add_argument("--playback-speed", type=float, default=1.0, 
                       help="Playback speed for video comparison (default: 1.0)")
    
    args = parser.parse_args()
    
    try:
        # Run analysis
        results = analyze_video_comparison(
            args.original_video,
            args.user_video,
            args.difficulty,
            args.sample_fps,
            args.output_dir
        )
        
        # Print results
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        
        if results["results"]:
            print(f"Found {len(results['results'])} keyframes with issues:")
            for i, result in enumerate(results["results"], 1):
                print(f"\n📍 Keyframe {i}:")
                print(f"   Frame: {result['frame_id']}")
                print(f"   Time: {result['timestamp']:.2f}s")
                print(f"   Score: {result['total_error']:.1f}°")
                print(f"   Issues: {len(result['joint_issues'])}")
                for suggestion in result['suggestions']:
                    print(f"   💡 {suggestion}")
        else:
            print("No significant issues found! Great job!")
        
        # Open video comparison if requested
        if args.view:
            print(f"\nOpening video comparison (press 'q' to exit)...")
            view_two_videos_with_pose(
                args.original_video,
                args.user_video,
                args.playback_speed
            )
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 