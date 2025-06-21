# Dance Analysis Backend - Pose Comparison Module

This module provides the core functionality for comparing dance poses between reference and user performances, calculating joint angle differences, and generating actionable feedback with support for multiple dance styles.

## Overview

The Pose Comparison + Keyframe Selector (Feature #2) analyzes dance performances by:
- Comparing user poses with reference poses frame-by-frame
- Calculating joint angle differences for arms, legs, torso, and head
- Supporting multiple dance styles with customized thresholds
- Identifying the most problematic keyframes (top 3 by total error)
- Generating human-readable suggestions for improvement

## Project Structure

```
dance_analysis_backend/
├── models.py          # Data models (PoseData, FrameComparisonResult, JointIssue)
├── compare.py         # Core comparison logic and helper functions
├── config.py          # Configuration management and dance style settings
├── app.py            # FastAPI application with endpoints
├── requirements.txt  # Python dependencies
├── test_compare.py   # Comprehensive test suite
├── example_usage.py  # Demonstration of all features
└── README.md         # This documentation
```

## Key Features

### 🎭 Strictness Support
- 1. Beginner (More Forgiving)
   Great for beginners - only flags major differences
   Threshold: 15.0°

2. Intermediate (Balanced)
   Balanced analysis for most dancers
   Threshold: 10.0°

3. Advanced (Precise)
   For advanced dancers - catches subtle differences
   Threshold: 6.0°

### 🔧 Expanded Joint Analysis
- **6 joint configurations** analyzed simultaneously
- **Arms**: Right and left arm angles (shoulder → elbow → wrist)
- **Legs**: Right and left leg angles (hip → knee → ankle)
- **Torso**: Body alignment (shoulder → hip → knee)

### ⚙️ Configuration Management
- Centralized configuration system
- Runtime threshold adjustment
- Dance style specific parameters
- Easy customization for new dance styles

## Data Models

### PoseData
Container for pose data from both reference and user performances:
```python
{
    "original": {
        "frame_1": {
            "right_shoulder": (100.0, 100.0),
            "right_elbow": (120.0, 80.0),
            # ... other keypoints
        }
    },
    "user": {
        "frame_1": {
            "right_shoulder": (100.0, 100.0),
            "right_elbow": (125.0, 75.0),
            # ... other keypoints
        }
    }
}
```

### FrameComparisonResult
Result of comparing poses for a specific frame:
```python
{
    "frame_id": "frame_1",
    "total_error": 45.2,
    "joint_issues": [
        {
            "joint": "right_arm",
            "delta_angle": 15.3,
            "suggestion": "Lower your right arm by 15.3°"
        }
    ],
    "suggestions": ["Lower your right arm by 15.3°"]
}
```

## Core Functions

### Main Function: `compare_all_frames(pose_data: PoseData) -> List[FrameComparisonResult]`

This is the primary function that:
1. Compares each frame between reference and user poses
2. Calculates joint angle differences for all 8 joint configurations
3. Identifies frames with significant pose errors (configurable threshold)
4. Ranks frames by total error and returns top 3

**Usage:**
```python
from models import PoseData
from compare import compare_all_frames

pose_data = PoseData(original=reference_poses, user=user_poses)
results = compare_all_frames(pose_data)
```

### Helper Functions

#### `calculate_angle(p1, p2, p3) -> float`
Calculates the angle between three points (p1 -> p2 -> p3) in degrees.

#### `generate_suggestion(joint: str, delta: float) -> str`
Generates human-readable suggestions for correcting joint angle differences.

## Joint Definitions

The module analyzes six key joint configurations:

1. **Right Arm**: `right_shoulder` → `right_elbow` → `right_wrist`
2. **Left Arm**: `left_shoulder` → `left_elbow` → `left_wrist`
3. **Right Leg**: `right_hip` → `right_knee` → `right_ankle`
4. **Left Leg**: `left_hip` → `left_knee` → `left_ankle`
5. **Torso**: `left_shoulder` → `left_hip` → `left_knee`
6. **Torso Alt**: `right_shoulder` → `right_hip` → `right_knee`

## Configuration

### Dance Style Configurations

Key parameters can be adjusted in `config.py`:

```python
DANCE_STYLES = {
    "ballet": {
        "angle_threshold": 8.0,  # More strict for ballet
        "priority_joints": ["right_arm", "left_arm", "right_leg", "left_leg"]
    },
    "hip_hop": {
        "angle_threshold": 12.0,  # More lenient for hip hop
        "priority_joints": ["torso", "right_leg", "left_leg"]
    },
    "contemporary": {
        "angle_threshold": 10.0,  # Standard threshold
        "priority_joints": ["right_arm", "left_arm", "torso", "head_tilt"]
    }
}
```

### Global Configuration

```python
ANGLE_THRESHOLD = 10.0      # Minimum angle difference to report (degrees)
TOP_N_FRAMES = 3           # Number of top problematic frames to return
```

## API Endpoints

### POST `/compare-poses`
Main endpoint for pose comparison analysis with dance style support.

**Request Body:**
```json
{
    "pose_data": {
        "original": {
            "frame_1": {
                "right_shoulder": [100.0, 100.0],
                "right_elbow": [120.0, 80.0],
                // ... other keypoints
            }
        },
        "user": {
            "frame_1": {
                "right_shoulder": [100.0, 100.0],
                "right_elbow": [125.0, 75.0],
                // ... other keypoints
            }
        }
    },
    "dance_style": "ballet"
}
```

**Response:**
```json
[
    {
        "frame_id": "frame_1",
        "total_error": 45.2,
        "joint_issues": [
            {
                "joint": "right_arm",
                "delta_angle": 15.3,
                "suggestion": "Lower your right arm by 15.3°"
            }
        ],
        "suggestions": ["Lower your right arm by 15.3°"]
    }
]
```

### GET `/dance-styles`
Get available dance styles and their configuration parameters.

**Response:**
```json
{
    "available_styles": ["ballet", "contemporary", "hip_hop"],
    "default_style": "contemporary",
    "configurations": {
        "ballet": {
            "angle_threshold": 8.0,
            "priority_joints": ["right_arm", "left_arm", "right_leg", "left_leg"]
        }
        // ... other styles
    }
}
```

### GET `/health`
Health check endpoint.

### POST `/test-comparison`
Test endpoint with sample data for development and testing.

## Installation and Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the FastAPI server:**
   ```bash
   python app.py
   ```
   Or with uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Testing and Examples

### Run Tests
```bash
python test_compare.py
```

### Run Example Demonstration
```bash
python example_usage.py
```

### Debug Analysis
```bash
python debug_test.py
```

## Integration Guide

### For Dev 1 (Pose Extractor)
Your pose extraction module should output data in the format expected by `PoseData`:
- Frame IDs as strings
- Keypoint coordinates as (x, y) tuples
- Required keypoints: All 17 keypoints defined in `config.KEYPOINTS`

### For Dev 3 (Frontend)
The API returns structured data that can be directly used for rendering:
- `frame_id`: Use for video scrubbing to problematic frames
- `total_error`: Display as a score or progress indicator
- `joint_issues`: Use for highlighting specific body parts
- `suggestions`: Display as user-friendly feedback text
- `dance_style`: Use to apply style-specific UI themes

### For Dev 4 (Frontend UI)
The response structure is consistent and includes:
- **Keyframe Score**: `total_error` field provides a numerical score
- **Joint Issues**: `joint_issues` array with specific joint names and angle differences
- **Suggestion Strings**: `suggestions` array with ready-to-display text
- **Dance Style Support**: Configure analysis sensitivity based on dance type

## Error Handling

The module includes comprehensive error handling:
- **Missing keypoints**: Gracefully skips frames with insufficient data
- **Invalid coordinates**: Validates point data before angle calculation
- **Empty results**: Returns empty list when no significant differences found
- **API errors**: Returns appropriate HTTP status codes with descriptive messages
- **Configuration errors**: Falls back to default settings if style config is invalid

## Performance Considerations

- **Efficient angle calculation**: Uses vector math for fast angle computation
- **Early termination**: Skips frames without required keypoints
- **Configurable thresholds**: Adjustable sensitivity for different use cases
- **Memory efficient**: Processes frames sequentially without storing all data
- **Thread-safe configuration**: Supports concurrent requests with different dance styles

## Future Enhancements

Potential improvements for future iterations:
- Support for additional joint configurations
- Dynamic threshold adjustment based on skill level
- Confidence scoring for pose detection quality
- Temporal analysis for movement patterns
- Custom suggestion templates for different dance genres
- Real-time analysis with WebSocket support
- Machine learning-based pose quality assessment
- Integration with video processing pipelines

## Contributing

When modifying this module:
1. Maintain the existing function signatures for API compatibility
2. Update documentation for any new parameters or return values
3. Add tests for new functionality
4. Ensure backward compatibility with existing data formats
5. Update configuration system for new dance styles
6. Test with multiple dance style configurations 
