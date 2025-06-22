#!/usr/bin/env python3
"""
Dance Analysis API

This module provides a Flask API to connect the frontend with the backend.
It handles video uploads, processes them using MediaPipe, and returns analysis results.
"""

import os
import json
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import werkzeug.utils

# Import the video processing function
from simple_video_processor import process_video_to_json
# Import the analysis function
from process_real_data import process_pose_file, run_analysis
from models import PoseData

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure allowed extensions
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Dance Analysis API is running"})

@app.route('/api/analyze', methods=['POST'])
def analyze_dance():
    """
    Analyze dance videos endpoint.
    
    Expects:
    - 'original' video file: The reference dance video
    - 'user' video file: The user's dance video
    - 'difficulty' (optional): Difficulty level (beginner, intermediate, advanced)
    - 'fps' (optional): Sample FPS for analysis
    
    Returns:
    - Analysis results JSON
    """
    # Check if both videos are provided
    if 'original' not in request.files or 'user' not in request.files:
        return jsonify({"error": "Both original and user videos are required"}), 400
    
    original_file = request.files['original']
    user_file = request.files['user']
    
    # Check if files are valid
    if not original_file.filename or not user_file.filename:
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(original_file.filename) or not allowed_file(user_file.filename):
        return jsonify({"error": "File type not allowed. Use mp4, mov, avi, or webm"}), 400
    
    # Get parameters
    difficulty = request.form.get('difficulty', 'intermediate')
    sample_fps = float(request.form.get('fps', 20.0))  # Default to 20 FPS for better analysis
    
    try:
        # Save uploaded files to temporary locations
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as original_temp:
            original_path = original_temp.name
            original_file.save(original_path)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as user_temp:
            user_path = user_temp.name
            user_file.save(user_path)
        
        # Process videos to extract pose data
        print(f"Processing original video at {sample_fps} FPS...")
        original_data = process_video_to_json(original_path, sample_fps)
        
        print(f"Processing user video at {sample_fps} FPS...")
        user_data = process_video_to_json(user_path, sample_fps)
        
        # Combine data into the expected format
        combined_data = {"original": original_data, "user": user_data}
        
        # Save combined data to a temporary JSON file
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as temp_json:
            json_path = temp_json.name
            json.dump(combined_data, temp_json, indent=2)
        
        # Process the pose data and get analysis results
        print(f"Analyzing dance with difficulty: {difficulty}...")
        analysis_results = process_pose_file(json_path, difficulty, sample_fps)
        
        # Clean up temporary files
        os.unlink(original_path)
        os.unlink(user_path)
        os.unlink(json_path)
        
        return jsonify(analysis_results)
    
    except Exception as e:
        # Clean up temporary files in case of error
        for path in [original_path, user_path, json_path]:
            if 'path' in locals() and os.path.exists(path):
                os.unlink(path)
        
        print(f"Error processing videos: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-json', methods=['POST'])
def analyze_json():
    """
    Analyze pre-processed JSON data endpoint.
    
    Expects:
    - JSON data with 'original' and 'user' sections
    - 'difficulty' (optional): Difficulty level (beginner, intermediate, advanced)
    - 'fps' (optional): Sample FPS for analysis
    
    Returns:
    - Analysis results JSON
    """
    # Check if JSON data is provided
    if not request.is_json:
        return jsonify({"error": "JSON data is required"}), 400
    
    data = request.json
    
    # Check if data has the required structure
    if 'original' not in data or 'user' not in data:
        return jsonify({"error": "JSON data must include 'original' and 'user' sections"}), 400
    
    # Get parameters
    difficulty = request.args.get('difficulty', 'intermediate')
    fps = float(request.args.get('fps', 20.0))  # Default to 20 FPS for better analysis
    
    try:
        # Create PoseData object
        pose_data = PoseData(original=data['original'], user=data['user'])
        
        # Run analysis
        analysis_results = run_analysis(pose_data, difficulty, fps)
        
        return jsonify(analysis_results)
    
    except Exception as e:
        print(f"Error analyzing JSON data: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5001))  # Changed to port 5001 to avoid conflict with AirPlay
    app.run(host='0.0.0.0', port=port, debug=True)
