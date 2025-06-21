"""
FastAPI application for dance analysis backend.

This module provides the main API endpoints for pose comparison and analysis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import PoseData, FrameComparisonResult
from compare import compare_all_frames, validate_pose_data, get_analysis_summary

app = FastAPI(
    title="Dance Analysis Backend",
    description="API for comparing dance poses and providing feedback",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Dance Analysis Backend API", "status": "healthy"}


@app.post("/compare-poses", response_model=List[FrameComparisonResult])
async def compare_poses(pose_data: PoseData, difficulty: str = "intermediate"):
    """
    Compare user poses with reference poses and return analysis results.
    
    This endpoint:
    1. Validates the input pose data
    2. Applies difficulty level specific configuration
    3. Compares all frames between reference and user performances
    4. Identifies the top 3 most problematic keyframes
    5. Returns detailed analysis with humanized suggestions
    
    Args:
        pose_data: PoseData object containing original and user pose dictionaries
        difficulty: Difficulty level (beginner, intermediate, advanced)
        
    Returns:
        List of FrameComparisonResult objects for the most problematic frames
        
    Raises:
        HTTPException: If pose data is invalid or comparison fails
    """
    try:
        # Validate input data
        if not validate_pose_data(pose_data):
            raise HTTPException(
                status_code=400, 
                detail="Invalid pose data: missing required keypoints for analysis"
            )
        
        # Apply difficulty level configuration
        from config import config
        difficulty_config = config.get_difficulty_config(difficulty)
        
        # Temporarily update configuration for this request
        original_threshold = config.ANGLE_THRESHOLD
        config.update_threshold(difficulty_config['angle_threshold'])
        
        # Update the compare module's threshold
        import compare
        compare.ANGLE_THRESHOLD = difficulty_config['angle_threshold']
        
        # Perform pose comparison
        results = compare_all_frames(pose_data)
        
        # Generate summary for logging/debugging
        summary = get_analysis_summary(results)
        print(f"Analysis completed for {difficulty} level: {summary}")
        
        # Restore original configuration
        config.update_threshold(original_threshold)
        compare.ANGLE_THRESHOLD = original_threshold
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during pose comparison: {str(e)}"
        )


@app.get("/difficulty-levels")
async def get_difficulty_levels():
    """
    Get available difficulty levels and their configuration parameters.
    
    Returns:
        Dictionary containing difficulty level configurations
    """
    from config import config
    return {
        "available_levels": list(config.DIFFICULTY_LEVELS.keys()),
        "default_level": "intermediate",
        "configurations": config.DIFFICULTY_LEVELS
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "compare_poses": "/compare-poses",
            "health": "/health"
        }
    }


# Example usage endpoint for testing
@app.post("/test-comparison")
async def test_comparison():
    """
    Test endpoint with sample pose data.
    
    This endpoint provides example pose data for testing the comparison functionality.
    """
    # Sample pose data for testing
    sample_pose_data = PoseData(
        original={
            "frame_1": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (120.0, 80.0),
                "right_wrist": (140.0, 60.0),
                "left_hip": (80.0, 150.0),
                "left_knee": (90.0, 200.0),
                "left_ankle": (100.0, 250.0),
                "left_ear": (95.0, 90.0),
                "left_eye": (100.0, 85.0)
            }
        },
        user={
            "frame_1": {
                "right_shoulder": (100.0, 100.0),
                "right_elbow": (125.0, 75.0),  # Different angle
                "right_wrist": (150.0, 50.0),  # Different angle
                "left_hip": (80.0, 150.0),
                "left_knee": (85.0, 210.0),    # Different angle
                "left_ankle": (95.0, 260.0),   # Different angle
                "left_ear": (90.0, 85.0),      # Different angle
                "left_eye": (95.0, 80.0)       # Different angle
            }
        }
    )
    
    try:
        results = compare_all_frames(sample_pose_data)
        summary = get_analysis_summary(results)
        
        return {
            "test_data": sample_pose_data,
            "results": results,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test comparison failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 