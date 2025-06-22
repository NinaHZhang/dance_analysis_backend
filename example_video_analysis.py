#!/usr/bin/env python3
"""
Example usage of the video processing tool.

This script demonstrates how to use the video_to_coordinates module
to analyze dance videos programmatically.
"""

from video_to_coordinates import analyze_video_comparison, process_video_to_json

def example_analysis():
    """Example of analyzing two dance videos."""
    
    # Example video paths (replace with your actual video files)
    original_video = "path/to/original_dance.mp4"
    user_video = "path/to/user_dance.mp4"
    
    try:
        # Run complete analysis
        results = analyze_video_comparison(
            original_video=original_video,
            user_video=user_video,
            difficulty="intermediate",
            sample_fps=2.0,
            output_dir="analysis_output"
        )
        
        # Print results
        print("Analysis completed successfully!")
        print(f"Found {len(results['results'])} keyframes with issues")
        
        # Access specific results
        for result in results['results']:
            print(f"Frame {result['frame_id']} at {result['timestamp']:.2f}s:")
            for suggestion in result['suggestions']:
                print(f"  - {suggestion}")
        
    except FileNotFoundError:
        print("Video files not found. Please update the paths in this script.")
    except Exception as e:
        print(f"Error during analysis: {e}")


def example_single_video():
    """Example of processing a single video to JSON."""
    
    video_path = "path/to/single_video.mp4"
    
    try:
        # Extract pose data from single video
        pose_data = process_video_to_json(video_path, sample_fps=2.0)
        
        print(f"Extracted pose data from {len(pose_data)} frames")
        print(f"Sample frame keys: {list(pose_data.keys())[:5]}")
        
        # Save to file
        import json
        with open("single_video_coordinates.json", "w") as f:
            json.dump(pose_data, f, indent=2)
        
        print("Saved coordinates to single_video_coordinates.json")
        
    except FileNotFoundError:
        print("Video file not found. Please update the path in this script.")
    except Exception as e:
        print(f"Error processing video: {e}")


if __name__ == "__main__":
    print("Video Analysis Examples")
    print("=" * 40)
    print()
    print("1. Complete analysis (requires two videos)")
    print("2. Single video processing")
    print()
    
    choice = input("Choose example (1 or 2): ").strip()
    
    if choice == "1":
        example_analysis()
    elif choice == "2":
        example_single_video()
    else:
        print("Invalid choice. Please run the script and choose 1 or 2.") 