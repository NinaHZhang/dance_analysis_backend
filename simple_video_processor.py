#!/usr/bin/env python3
"""
Simple video processing module for dance analysis.

This module provides the core functionality to extract pose keypoints from videos
and convert them to JSON format with normalized coordinates.
"""

import cv2
import mediapipe as mp
import numpy as np
import json

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
    Includes an additional midpoint_shoulder landmark.
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

                # compute midpoint between shoulders
                ls = results.pose_landmarks.landmark[
                    mp_pose.PoseLandmark.LEFT_SHOULDER.value
                ]
                rs = results.pose_landmarks.landmark[
                    mp_pose.PoseLandmark.RIGHT_SHOULDER.value
                ]
                mid_x = 1.0 - ((ls.x + rs.x) / 2)
                mid_y = 1.0 - ((ls.y + rs.y) / 2)
                coords["midpoint_shoulder"] = [mid_x, mid_y]

            data[key] = coords
            frame_idx += 1
            
            # Progress indicator
            if frame_idx % 10 == 0:
                print(f"Processed {frame_idx} frames...")

    cap.release()
    print(f"Extracted pose data from {len(data)} frames")
    return data

# Simple example usage
if __name__ == "__main__":
    import sys
    import os
    
    video_path = "ninoriginal.mp4"
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Process the video
    print(f"Processing video: {video_path}")
    data = process_video_to_json(video_path, sample_fps=1.0)
    
    # Print the JSON output
    print("\nJSON output:")
    print(json.dumps(data, indent=2))
