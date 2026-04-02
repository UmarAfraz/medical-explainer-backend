"""
AI Service Module - OpenAI GPT-4 Integration
Generates patient-friendly explanations using OpenAI's GPT-4 API
"""

import logging
import os
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIExplainer:
    """Handles AI-powered explanation generation using OpenAI GPT-4"""
    
    def __init__(self):
        """Initialize AI service with OpenAI configuration"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("AI Service initialized with OpenAI GPT-4")
    
    def generate_explanation(
        self,
        parsed_data: Dict[str, Any],
        report_type: str = "unknown"
    ) -> str:
        """
        Generate patient-friendly explanation using GPT-4
        
        Args:
            parsed_data: Parsed medical report data
            report_type: Type of report (blood_test, imaging, etc.)
            
        Returns:
            Patient-friendly explanation text
        """
        try:
            if not self.client:
                return self._get_fallback_explanation(parsed_data, report_type)
            
            # Build the prompt
            prompt = self._build_prompt(parsed_data, report_type)
            
            # Call OpenAI API
            explanation = self._call_openai(prompt)
            
            # Add disclaimer
            explanation_with_disclaimer = self._add_disclaimer(explanation)
            
            logger.info("Successfully generated explanation using GPT-4")
            return explanation_with_disclaimer
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return self._get_fallback_explanation(parsed_data, report_type)
    
    def _build_prompt(self, parsed_data: Dict[str, Any], report_type: str) -> str:
        """Build the prompt for GPT-4"""
        
        # Extract test results if available
        tests_info = ""
        if 'tests' in parsed_data and parsed_data['tests']:
            tests_info = "\n\nTest Results:\n"
            for test in parsed_data['tests']:
                test_name = test.get('test_name') or test.get('full_name') or 'Unknown'
                value = test.get('value', 'N/A')
                unit = test.get('unit', '')
                ref_min = test.get('reference_min', '')
                ref_max = test.get('reference_max', '')
                normal_range = f"{ref_min}-{ref_max}" if ref_min and ref_max else 'N/A'
                status = test.get('status', 'Unknown')
                
                tests_info += f"- {test_name}: {value} {unit}"
                tests_info += f" [Normal: {normal_range}]"
                tests_info += f" - Status: {status}\n"
        
        # Build comprehensive prompt
        prompt = f"""You are a medical expert explaining test results to patients in simple, clear language.

IMPORTANT INSTRUCTIONS:
1. Explain in terms an 8th grader can understand
2. Use everyday language, not medical jargon
3. Be reassuring and clear
4. Explain what each test measures and why it matters
5. Explain what the results mean for the patient's health
6. Do NOT provide diagnosis or treatment recommendations
7. Do NOT suggest medications
8. Always encourage consulting with their healthcare provider

Report Type: {report_type}
{tests_info}

Please provide a patient-friendly explanation of these medical test results. Focus on:
- What each test measures in simple terms
- Whether results are normal or abnormal
- What abnormal results might indicate (without diagnosing)
- General health context

Keep the explanation clear, concise, and reassuring."""

        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API to generate response"""
        
        try:
            logger.info("Calling OpenAI GPT-4 API")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful medical assistant who explains medical reports in simple, patient-friendly language. You never diagnose or recommend treatment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            explanation = response.choices[0].message.content.strip()
            
            if explanation:
                logger.info("Successfully received response from GPT-4")
                return explanation
            else:
                raise Exception("Empty response from GPT-4")
                
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _add_disclaimer(self, explanation: str) -> str:
        """Add medical disclaimer to explanation"""
        disclaimer = "\n\n" + "="*80 + "\n"
        disclaimer += "⚠️ IMPORTANT DISCLAIMER\n"
        disclaimer += "="*80 + "\n"
        disclaimer += "This explanation is for educational purposes only and is NOT medical advice.\n"
        disclaimer += "Always consult your healthcare provider for:\n"
        disclaimer += "- Medical diagnosis\n"
        disclaimer += "- Treatment recommendations\n"
        disclaimer += "- Medication decisions\n"
        disclaimer += "- Any health concerns\n\n"
        disclaimer += "If you have questions about your results, please contact your doctor.\n"
        disclaimer += "="*80
        
        return explanation + disclaimer
    
    def _get_fallback_explanation(
        self,
        parsed_data: Dict[str, Any],
        report_type: str
    ) -> str:
        """Provide fallback explanation if AI fails"""
        
        explanation = "MEDICAL REPORT SUMMARY\n" + "="*80 + "\n\n"
        
        if report_type == "blood_test":
            explanation += "Blood Test Results:\n\n"
            
            if 'tests' in parsed_data and parsed_data['tests']:
                normal_count = sum(1 for t in parsed_data['tests'] if t.get('status') == 'normal')
                abnormal_count = sum(1 for t in parsed_data['tests'] if t.get('status') == 'abnormal')
                
                explanation += f"Total Tests: {len(parsed_data['tests'])}\n"
                explanation += f"Normal Results: {normal_count}\n"
                explanation += f"Abnormal Results: {abnormal_count}\n\n"
                
                if abnormal_count > 0:
                    explanation += "Tests with abnormal values:\n"
                    for test in parsed_data['tests']:
                        if test.get('status') == 'abnormal':
                            explanation += f"- {test.get('name')}: {test.get('value')} {test.get('unit')}\n"
                            explanation += f"  Normal range: {test.get('normal_range')}\n"
        
        elif report_type == "imaging":
            explanation += "Imaging Report Summary:\n\n"
            explanation += "An imaging study was performed. "
            explanation += "Please review the detailed findings with your healthcare provider.\n"
        
        explanation += "\n" + "="*80 + "\n"
        explanation += "⚠️ AI service temporarily unavailable.\n"
        explanation += "Please consult your healthcare provider to discuss these results.\n"
        explanation += "="*80
        
        return explanation
    
    def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection and return status"""
        try:
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "OpenAI API key not configured"
                }
            
            if not self.client:
                return {
                    "status": "error",
                    "message": "OpenAI client not initialized"
                }
            
            # Test with a simple API call
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "connected",
                "model": "gpt-4",
                "message": "OpenAI API connection successful"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"OpenAI API error: {str(e)}"
            }


# Singleton instance
ai_explainer = AIExplainer()


def explain_report(parsed_data: Dict[str, Any], report_type: str = "unknown") -> str:
    """
    Main function to generate explanation
    
    Args:
        parsed_data: Parsed medical report data
        report_type: Type of report
        
    Returns:
        Patient-friendly explanation
    """
    return ai_explainer.generate_explanation(parsed_data, report_type)


def test_ai_service() -> Dict[str, Any]:
    """Test AI service connection"""
    return ai_explainer.test_connection()
