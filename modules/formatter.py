"""
Response Formatter Module for Medical Report Explanation System
Formats AI-generated explanations for display
"""

import logging
from typing import Dict
from config import Config
from modules.utils import ResponseHelper

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Format explanations for user-friendly display"""
    
    def __init__(self):
        """Initialize formatter"""
        self.response_helper = ResponseHelper()
    
    def format_explanation(self, explanation: str, parsed_data: Dict, 
                          include_disclaimer: bool = True) -> Dict:
        """
        Format complete explanation response
        
        Args:
            explanation: AI-generated explanation
            parsed_data: Original parsed data
            include_disclaimer: Whether to add disclaimer
            
        Returns:
            Formatted response dictionary
        """
        # Add disclaimer if requested
        if include_disclaimer:
            explanation = self.response_helper.add_disclaimer(explanation)
        
        # Build response structure
        formatted_response = {
            'explanation': explanation,
            'parsed_data': self._sanitize_parsed_data(parsed_data),
            'summary': self._generate_summary(parsed_data),
            'metadata': self._generate_metadata(parsed_data)
        }
        
        return formatted_response
    
    def _sanitize_parsed_data(self, parsed_data: Dict) -> Dict:
        """
        Remove internal/technical fields from parsed data
        
        Args:
            parsed_data: Raw parsed data
            
        Returns:
            Sanitized data safe for user display
        """
        # Create a copy to avoid modifying original
        sanitized = {}
        
        report_type = parsed_data.get('report_type')
        sanitized['report_type'] = report_type
        
        if report_type == 'blood_test':
            # Include relevant test information
            tests = []
            for test in parsed_data.get('tests', []):
                tests.append({
                    'name': test.get('full_name', test.get('test_name')),
                    'value': test.get('value'),
                    'unit': test.get('unit'),
                    'status': test.get('status'),
                    'normal_range': self._format_normal_range(
                        test.get('reference_min'),
                        test.get('reference_max'),
                        test.get('unit')
                    )
                })
            
            sanitized['tests'] = tests
            sanitized['abnormal_count'] = len(parsed_data.get('abnormal_flags', []))
            
        elif report_type == 'imaging':
            sanitized['modality'] = parsed_data.get('modality')
            sanitized['impression'] = parsed_data.get('impression')
            sanitized['has_abnormalities'] = parsed_data.get('has_abnormalities', False)
        
        return sanitized
    
    def _format_normal_range(self, min_val: float, max_val: float, 
                            unit: str) -> str:
        """
        Format normal range as readable string
        
        Args:
            min_val: Minimum normal value
            max_val: Maximum normal value
            unit: Unit of measurement
            
        Returns:
            Formatted range string
        """
        if min_val is None or max_val is None:
            return "Range not available"
        
        return f"{min_val}-{max_val} {unit}"
    
    def _generate_summary(self, parsed_data: Dict) -> Dict:
        """
        Generate summary of report
        
        Args:
            parsed_data: Parsed report data
            
        Returns:
            Summary dictionary
        """
        report_type = parsed_data.get('report_type')
        summary = {
            'report_type': report_type
        }
        
        if report_type == 'blood_test':
            total_tests = len(parsed_data.get('tests', []))
            abnormal_count = len(parsed_data.get('abnormal_flags', []))
            normal_count = total_tests - abnormal_count
            
            summary.update({
                'total_tests': total_tests,
                'normal_results': normal_count,
                'abnormal_results': abnormal_count,
                'categories': parsed_data.get('summary', {}).get('test_categories', [])
            })
            
            # Add interpretation
            if abnormal_count == 0:
                summary['overall_status'] = 'All results within normal range'
            else:
                summary['overall_status'] = f'{abnormal_count} result(s) outside normal range - discuss with doctor'
        
        elif report_type == 'imaging':
            summary.update({
                'modality': parsed_data.get('modality', 'Unknown'),
                'findings_noted': len(parsed_data.get('key_findings', [])) > 0,
                'has_abnormalities': parsed_data.get('has_abnormalities', False)
            })
            
            if not parsed_data.get('has_abnormalities'):
                summary['overall_status'] = 'No significant abnormalities noted'
            else:
                summary['overall_status'] = 'Findings noted - review with doctor'
        
        return summary
    
    def _generate_metadata(self, parsed_data: Dict) -> Dict:
        """
        Generate metadata about the explanation
        
        Args:
            parsed_data: Parsed report data
            
        Returns:
            Metadata dictionary
        """
        import datetime
        
        metadata = {
            'generated_at': datetime.datetime.now().isoformat(),
            'ai_model': Config.OPENAI_MODEL,
            'version': '1.0.0',
            'disclaimer_included': Config.INCLUDE_DISCLAIMER
        }
        
        return metadata
    
    def format_error_response(self, error_message: str, 
                             error_type: str = 'general') -> Dict:
        """
        Format error response
        
        Args:
            error_message: Error description
            error_type: Type of error
            
        Returns:
            Formatted error response
        """
        return {
            'success': False,
            'error': {
                'type': error_type,
                'message': error_message
            }
        }
    
    def format_for_html(self, explanation: str) -> str:
        """
        Format explanation for HTML display
        
        Args:
            explanation: Plain text explanation
            
        Returns:
            HTML-formatted explanation
        """
        # Convert markdown-style headers to HTML
        html = explanation.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n')
        
        # Convert bullet points
        html = html.replace('\n- ', '\n<li>').replace('</li>\n<li>', '</li>\n<li>')
        
        # Convert bold text
        html = html.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
        
        # Add line breaks
        html = html.replace('\n\n', '<br><br>')
        
        # Wrap disclaimer in special div
        if '⚠️ IMPORTANT DISCLAIMER' in html:
            parts = html.split('⚠️ IMPORTANT DISCLAIMER')
            if len(parts) == 2:
                html = parts[0] + '<div class="disclaimer-box">⚠️ IMPORTANT DISCLAIMER' + parts[1] + '</div>'
        
        return html
    
    def format_for_download(self, explanation: str, parsed_data: Dict) -> str:
        """
        Format explanation for downloadable text file
        
        Args:
            explanation: Generated explanation
            parsed_data: Parsed report data
            
        Returns:
            Formatted text for download
        """
        import datetime
        
        output = "=" * 60 + "\n"
        output += "MEDICAL REPORT EXPLANATION\n"
        output += "Generated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        output += "=" * 60 + "\n\n"
        
        # Add summary
        summary = self._generate_summary(parsed_data)
        output += "SUMMARY:\n"
        output += "-" * 60 + "\n"
        for key, value in summary.items():
            output += f"{key.replace('_', ' ').title()}: {value}\n"
        output += "\n"
        
        # Add explanation
        output += "DETAILED EXPLANATION:\n"
        output += "-" * 60 + "\n"
        output += explanation + "\n\n"
        
        output += "=" * 60 + "\n"
        output += "This explanation was generated by an AI system and is for\n"
        output += "educational purposes only. Always consult with your healthcare\n"
        output += "provider for medical advice.\n"
        output += "=" * 60 + "\n"
        
        return output


# Example usage
if __name__ == "__main__":
    formatter = ResponseFormatter()
    
    # Test with sample data
    sample_explanation = """# Your Blood Test Results

Your Complete Blood Count (CBC) shows:

**White Blood Cells (WBC)**: 7.5 × 10^9/L - NORMAL
- What it measures: Cells that fight infection
- Your result is within the healthy range of 4.0-11.0

⚠️ IMPORTANT DISCLAIMER:
This is educational information only."""
    
    sample_parsed = {
        'report_type': 'blood_test',
        'tests': [
            {
                'test_name': 'WBC',
                'full_name': 'White Blood Cells',
                'value': 7.5,
                'unit': '10^9/L',
                'status': 'normal',
                'reference_min': 4.0,
                'reference_max': 11.0
            }
        ],
        'abnormal_flags': []
    }
    
    formatted = formatter.format_explanation(sample_explanation, sample_parsed)
    print("Formatted response structure:")
    print(f"Keys: {formatted.keys()}")
    print(f"\nSummary: {formatted['summary']}")
