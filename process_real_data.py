"""
Script to process real pose data files with time-series joint coordinates.

This script can handle:
- JSON files with frame-by-frame pose data
- CSV files with time-series coordinates
- Different data formats and structures
- Real pose detection output from various systems
- Interactive difficulty level selection
"""

import json
import csv
import os
from typing import Dict, List, Tuple, Any
from models import PoseData
from compare import compare_all_frames, get_analysis_summary
from config import config


def detect_file_format(file_path: str) -> str:
    """Detect the format of the pose data file."""
    if file_path.endswith('.json'):
        return 'json'
    elif file_path.endswith('.csv'):
        return 'csv'
    else:
        # Try to read as JSON first, then CSV
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            return 'json'
        except:
            return 'csv'


def parse_json_pose_data(file_path: str) -> PoseData:
    """
    Parse JSON pose data files.
    
    Supports multiple JSON formats:
    1. Standard format with 'original' and 'user' sections
    2. Array format with frame objects
    3. Nested format with time-based structure
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Try different JSON structures
    if isinstance(data, dict):
        if 'original' in data and 'user' in data:
            # Standard format
            return _parse_standard_json(data)
        elif 'frames' in data or 'poses' in data:
            # Array format
            return _parse_array_json(data)
        else:
            # Try to infer structure
            return _parse_inferred_json(data)
    elif isinstance(data, list):
        # List of frames
        return _parse_list_json(data)
    else:
        raise ValueError(f"Unsupported JSON structure in {file_path}")


def _parse_standard_json(data: Dict) -> PoseData:
    """Parse standard JSON format with 'original' and 'user' sections."""
    def convert_coordinates(pose_dict):
        converted = {}
        for frame_id, frame_data in pose_dict.items():
            converted[frame_id] = {}
            for keypoint, coords in frame_data.items():
                if isinstance(coords, list) and len(coords) >= 2:
                    converted[frame_id][keypoint] = tuple(coords[:2])  # Take only x, y
                elif isinstance(coords, dict) and 'x' in coords and 'y' in coords:
                    converted[frame_id][keypoint] = (coords['x'], coords['y'])
        return converted
    
    return PoseData(
        original=convert_coordinates(data["original"]),
        user=convert_coordinates(data["user"])
    )


def _parse_array_json(data: Dict) -> PoseData:
    """Parse JSON with array of frames."""
    frames_key = 'frames' if 'frames' in data else 'poses'
    frames = data[frames_key]
    
    original_frames = {}
    user_frames = {}
    
    for i, frame in enumerate(frames):
        frame_id = f"frame_{i+1}"
        
        # Extract original and user poses from frame
        if 'original' in frame and 'user' in frame:
            original_frames[frame_id] = _extract_keypoints(frame['original'])
            user_frames[frame_id] = _extract_keypoints(frame['user'])
        elif 'cover' in frame and 'reference' in frame:
            original_frames[frame_id] = _extract_keypoints(frame['reference'])
            user_frames[frame_id] = _extract_keypoints(frame['cover'])
    
    return PoseData(original=original_frames, user=user_frames)


def _parse_inferred_json(data: Dict) -> PoseData:
    """Try to infer the structure of the JSON data."""
    # Look for common patterns
    original_frames = {}
    user_frames = {}
    
    for key, value in data.items():
        if isinstance(value, dict):
            # Check if this looks like pose data
            if any(kp in value for kp in ['right_shoulder', 'left_shoulder']):
                if 'original' in key.lower() or 'reference' in key.lower():
                    original_frames[key] = _extract_keypoints(value)
                elif 'user' in key.lower() or 'cover' in key.lower():
                    user_frames[key] = _extract_keypoints(value)
                else:
                    # Assume it's user data if we can't determine
                    user_frames[key] = _extract_keypoints(value)
    
    return PoseData(original=original_frames, user=user_frames)


def _parse_list_json(data: List) -> PoseData:
    """Parse JSON list of frames."""
    original_frames = {}
    user_frames = {}
    
    for i, frame in enumerate(data):
        frame_id = f"frame_{i+1}"
        if isinstance(frame, dict):
            if 'original' in frame and 'user' in frame:
                original_frames[frame_id] = _extract_keypoints(frame['original'])
                user_frames[frame_id] = _extract_keypoints(frame['user'])
    
    return PoseData(original=original_frames, user=user_frames)


def _extract_keypoints(pose_data: Dict) -> Dict[str, Tuple[float, float]]:
    """Extract keypoints from pose data in various formats."""
    keypoints = {}
    
    for key, value in pose_data.items():
        if isinstance(value, list) and len(value) >= 2:
            keypoints[key] = tuple(value[:2])
        elif isinstance(value, dict):
            if 'x' in value and 'y' in value:
                keypoints[key] = (value['x'], value['y'])
            elif 'position' in value:
                pos = value['position']
                if isinstance(pos, list) and len(pos) >= 2:
                    keypoints[key] = tuple(pos[:2])
    
    return keypoints


def parse_csv_pose_data(file_path: str) -> PoseData:
    """
    Parse CSV pose data files.
    
    Supports CSV formats with:
    - Time-based columns
    - Joint coordinate columns
    - Multiple dancer data
    """
    original_frames = {}
    user_frames = {}
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader):
            frame_id = f"frame_{row_num + 1}"
            
            # Extract keypoints from row
            original_keypoints = {}
            user_keypoints = {}
            
            for key, value in row.items():
                if key.startswith('original_') or key.startswith('reference_'):
                    joint_name = key.replace('original_', '').replace('reference_', '')
                    if '_x' in joint_name:
                        joint_base = joint_name.replace('_x', '')
                        x_val = float(value) if value else 0.0
                        y_key = key.replace('_x', '_y')
                        y_val = float(row.get(y_key, 0)) if row.get(y_key) else 0.0
                        original_keypoints[joint_base] = (x_val, y_val)
                
                elif key.startswith('user_') or key.startswith('cover_'):
                    joint_name = key.replace('user_', '').replace('cover_', '')
                    if '_x' in joint_name:
                        joint_base = joint_name.replace('_x', '')
                        x_val = float(value) if value else 0.0
                        y_key = key.replace('_x', '_y')
                        y_val = float(row.get(y_key, 0)) if row.get(y_key) else 0.0
                        user_keypoints[joint_base] = (x_val, y_val)
            
            if original_keypoints:
                original_frames[frame_id] = original_keypoints
            if user_keypoints:
                user_frames[frame_id] = user_keypoints
    
    return PoseData(original=original_frames, user=user_frames)


def select_difficulty_level() -> str:
    """Interactive difficulty level selection."""
    print("\n🎯 SELECT DIFFICULTY LEVEL")
    print("=" * 40)
    
    for i, (key, level) in enumerate(config.DIFFICULTY_LEVELS.items(), 1):
        print(f"{i}. {level['name']}")
        print(f"   {level['description']}")
        print(f"   Threshold: {level['angle_threshold']}°")
        print()
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            if choice == "1":
                return "beginner"
            elif choice == "2":
                return "intermediate"
            elif choice == "3":
                return "advanced"
            else:
                print("Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\nExiting...")
            exit()
        except:
            print("Invalid input. Please try again.")


def select_fps() -> float:
    """Interactive FPS selection."""
    print("\n🎬 SELECT FRAME RATE (FPS)")
    print("=" * 40)
    print("Common frame rates:")
    print("1. 24 FPS (Film)")
    print("2. 30 FPS (Video)")
    print("3. 60 FPS (High-speed)")
    print("4. Custom FPS")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            if choice == "1":
                return 24.0
            elif choice == "2":
                return 30.0
            elif choice == "3":
                return 60.0
            elif choice == "4":
                while True:
                    try:
                        custom_fps = float(input("Enter custom FPS (e.g., 25.0): ").strip())
                        if custom_fps > 0:
                            return custom_fps
                        else:
                            print("FPS must be greater than 0")
                    except ValueError:
                        print("Please enter a valid number")
            else:
                print("Please enter 1, 2, 3, or 4")
        except KeyboardInterrupt:
            print("\nExiting...")
            exit()
        except:
            print("Invalid input. Please try again.")


def calculate_timestamp(frame_id: str, fps: float = 30.0) -> float:
    """Calculate timestamp from frame ID."""
    try:
        frame_num = int(frame_id.replace('frame_', ''))
        return (frame_num - 1) / fps
    except:
        return 0.0


def process_pose_file(file_path: str, difficulty: str = "intermediate", fps: float = 30.0) -> Dict:
    """
    Process a pose data file and return analysis results.
    
    Args:
        file_path: Path to the pose data file
        difficulty: Difficulty level for analysis
        fps: Frame rate for timestamp calculation
    
    Returns:
        Dictionary with analysis results
    """
    print(f"📁 Processing file: {file_path}")
    
    # Detect file format
    file_format = detect_file_format(file_path)
    print(f"📄 Detected format: {file_format}")
    
    # Parse the file
    try:
        if file_format == 'json':
            pose_data = parse_json_pose_data(file_path)
        else:
            pose_data = parse_csv_pose_data(file_path)
        
        print(f"✅ Successfully parsed {len(pose_data.original)} original frames and {len(pose_data.user)} user frames")
        
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        return {"error": str(e)}
    
    # Validate data
    if not pose_data.original or not pose_data.user:
        print("❌ No valid pose data found in file")
        return {"error": "No valid pose data found"}
    
    # Run analysis
    return run_analysis(pose_data, difficulty, fps)


def run_analysis(pose_data: PoseData, difficulty: str = "intermediate", fps: float = 30.0) -> Dict:
    """Run dance analysis on pose data with difficulty-based thresholds."""
    print(f"🎭 Analyzing with {difficulty} difficulty...")
    print(f"🎬 Using {fps} FPS for timestamp calculation")
    
    # Get difficulty configuration
    difficulty_config = config.get_difficulty_config(difficulty)
    print(f"⚙️  Using threshold: {difficulty_config['angle_threshold']}°")
    
    # Run analysis with difficulty level
    results = compare_all_frames(pose_data, difficulty)
    summary = get_analysis_summary(results)
    
    # Format results
    analysis_results = {
        "difficulty": difficulty,
        "difficulty_name": difficulty_config['name'],
        "threshold": difficulty_config['angle_threshold'],
        "fps": fps,
        "frames_analyzed": len(pose_data.original),
        "problematic_frames": len(results),
        "total_error": summary.get('total_error', 0),
        "average_error": summary.get('average_error', 0),
        "results": []
    }
    
    for result in results:
        frame_result = {
            "frame_id": result.frame_id,
            "timestamp": calculate_timestamp(result.frame_id, fps),
            "score": result.total_error,
            "joint_issues": [
                {
                    "joint": issue.joint,
                    "delta_angle": issue.delta_angle,
                    "suggestion": issue.suggestion
                }
                for issue in result.joint_issues
            ],
            "suggestions": result.suggestions
        }
        analysis_results["results"].append(frame_result)
    
    return analysis_results


def print_analysis_results(results: Dict):
    """Print analysis results in a user-friendly format."""
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    print(f"\n📊 ANALYSIS RESULTS")
    print(f"   Difficulty: {results['difficulty_name']}")
    print(f"   Threshold: {results['threshold']}°")
    print(f"   Frame Rate: {results.get('fps', 30.0)} FPS")
    print(f"   Frames Analyzed: {results['frames_analyzed']}")
    print(f"   Keyframes Found: {results['problematic_frames']}")
    
    if results['results']:
        print(f"\n🎯 KEYFRAME BREAKDOWN:")
        print("-" * 60)
        
        for i, result in enumerate(results['results'], 1):
            print(f"\n📍 Keyframe {i}:")
            print(f"   Frame: {result['frame_id']}")
            print(f"   Time: {result['timestamp']:.2f}s")
            print(f"   Score: {result['score']:.1f}°")
            print(f"   Issues: {len(result['joint_issues'])}")
            
            for issue in result['joint_issues']:
                print(f"   💡 {issue['suggestion']}")
    else:
        print("   ✅ No significant issues found!")


def main():
    """Main function to process pose data files."""
    print("🕺 DANCE POSE ANALYSIS")
    print("=" * 50)
    
    # Look for pose data files in current directory
    pose_files = []
    for file in os.listdir('.'):
        if file.endswith(('.json', '.csv')):
            # Check for various dance/pose related keywords
            file_lower = file.lower()
            if any(keyword in file_lower for keyword in ['pose', 'dance', 'arm', 'nin', 'vertopal']):
                pose_files.append(file)
    
    if not pose_files:
        print("📄 No pose data files found in current directory.")
        print("\n💡 Supported file formats:")
        print("   • JSON files with 'original' and 'user' pose data")
        print("   • CSV files with joint coordinates")
        print("   • Files with 'pose' in the filename")
        print("\n📁 Place your pose data file in this directory and run again.")
        return
    
    print(f"📁 Found {len(pose_files)} pose data file(s):")
    for i, file in enumerate(pose_files, 1):
        print(f"   {i}. {file}")
    
    # Select difficulty level
    difficulty = select_difficulty_level()
    
    # Select FPS
    fps = select_fps()
    
    # Process each file
    for file_path in pose_files:
        print(f"\n{'='*60}")
        print(f"Processing: {file_path}")
        print(f"{'='*60}")
        
        results = process_pose_file(file_path, difficulty, fps)
        print_analysis_results(results)


if __name__ == "__main__":
    main() 