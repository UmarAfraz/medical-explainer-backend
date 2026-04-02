"""
Main Flask Application for Medical Report Explanation System
Provides REST API endpoints for medical report processing
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import get_config, Config
from modules import ReportParser, InputValidator, AIExplainer, ResponseFormatter
from modules.utils import FileHandler, initialize_data

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
config_class = get_config()
app.config.from_object(config_class)

# Enable CORS for frontend access
CORS(app, origins=Config.CORS_ORIGINS)

# Set up logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize components
try:
    Config.validate_config()
    initialize_data()
    
    parser = ReportParser()
    validator = InputValidator()
    ai_explainer = AIExplainer()
    formatter = ResponseFormatter()
    
    logger.info("Application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    raise


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON response with system health status
    """
    try:
        health_status = validator.validate_health_check()
        
        # Test AI API connection
        try:
            if ai_explainer.test_connection().get("status") == "connected":
                health_status['checks']['openai_api'] = 'connected'
            else:
                health_status['checks']['openai_api'] = 'failed'
                health_status['status'] = 'unhealthy'
        except:
            health_status['checks']['openai_api'] = 'error'
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/api/explain', methods=['POST'])
def explain_report():
    """
    Main endpoint to process and explain medical reports
    
    Request Body:
        - report_text (str): Text content of report
        - report_type (str, optional): 'blood_test', 'imaging', or 'auto'
        - include_disclaimer (bool, optional): Include safety disclaimer
    
    Returns:
        JSON response with explanation and parsed data
    """
    try:
        # Get request data
        if request.is_json:
            request_data = request.get_json()
        else:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        logger.info("Received explain request")
        
        # Validate request
        is_valid, error, validated_data = validator.validate_api_request(request_data)
        if not is_valid:
            logger.warning(f"Validation failed: {error}")
            return jsonify({'error': error}), 400
        
        report_text = validated_data['report_text']
        report_type = validated_data['report_type']
        include_disclaimer = validated_data['include_disclaimer']
        
        logger.info(f"Processing {report_type} report")
        
        # Parse the report
        try:
            parsed_data = parser.parse_report(report_text, report_type)
            logger.info(f"Successfully parsed report: {parsed_data.get('report_type')}")
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return jsonify({
                'error': 'Failed to parse report',
                'details': str(e)
            }), 500
        
        # Generate AI explanation
        try:
            explanation = ai_explainer.generate_explanation(parsed_data)
            logger.info("Successfully generated explanation")
        except Exception as e:
            logger.error(f"AI explanation failed: {e}")
            return jsonify({
                'error': 'Failed to generate explanation',
                'details': str(e)
            }), 500
        
        # Format response
        try:
            formatted_response = formatter.format_explanation(
                explanation,
                parsed_data,
                include_disclaimer
            )
            logger.info("Successfully formatted response")
        except Exception as e:
            logger.error(f"Formatting failed: {e}")
            return jsonify({
                'error': 'Failed to format response',
                'details': str(e)
            }), 500
        
        # Return success response
        return jsonify({
            'success': True,
            'data': formatted_response
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in explain_report: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to upload and process file
    
    Form Data:
        - file: Medical report file (PDF, TXT, DOCX)
        - report_type (optional): 'blood_test', 'imaging', or 'auto'
    
    Returns:
        JSON response with explanation
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, error = validator.validate_file_upload(file)
        if not is_valid:
            logger.warning(f"File validation failed: {error}")
            return jsonify({'error': error}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Create upload folder if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        file.save(temp_path)
        logger.info(f"File saved: {filename}")
        
        try:
            # Read file content
            file_handler = FileHandler()
            report_text = file_handler.read_file(temp_path)
            
            # Get report type from form data
            report_type = request.form.get('report_type', 'auto')
            
            # Validate text content
            is_valid, error = validator.validate_text_content(report_text)
            if not is_valid:
                return jsonify({'error': error}), 400
            
            # Sanitize text
            report_text = validator.sanitize_text(report_text)
            
            # Auto-detect report type if needed
            if report_type == 'auto':
                report_type = validator.detect_report_type(report_text)
            
            # Parse report
            parsed_data = parser.parse_report(report_text, report_type)
            
            # Generate explanation
            explanation = ai_explainer.generate_explanation(parsed_data)
            
            # Format response
            formatted_response = formatter.format_explanation(
                explanation,
                parsed_data,
                include_disclaimer=True
            )
            
            return jsonify({
                'success': True,
                'data': formatted_response
            }), 200
            
        finally:
            # Clean up: delete temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Temporary file deleted: {filename}")
    
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return jsonify({
            'error': 'File processing failed',
            'details': str(e)
        }), 500


@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """
    Simple test endpoint to verify API is running
    
    Returns:
        JSON response with test message
    """
    return jsonify({
        'message': 'Medical Report Explanation API is running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'explain': '/api/explain (POST)',
            'upload': '/api/upload (POST)',
            'test': '/api/test (GET)'
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on the server.'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred.'
    }), 500


# Run the application
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    # Run Flask development server
    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
