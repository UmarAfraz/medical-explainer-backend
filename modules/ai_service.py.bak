"""
AI Service Module - Ollama Integration
Generates patient-friendly explanations using local Ollama (Meditron model)
"""

import logging
import requests
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIExplainer:
    """Handles AI-powered explanation generation using Ollama"""
    
    def __init__(self):
        """Initialize AI service with Ollama configuration"""
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.2"
        logger.info(f"AI Service initialized with Ollama model: {self.model_name}")
        
        # Verify Ollama is running
        if not self._check_ollama_available():
            logger.warning("Ollama service not available at startup")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_explanation(
        self,
        parsed_data: Dict[str, Any],
        report_type: str = "unknown"
    ) -> str:
        """
        Generate patient-friendly explanation using Ollama
        
        Args:
            parsed_data: Parsed medical report data
            report_type: Type of report (blood_test, imaging, etc.)
            
        Returns:
            Patient-friendly explanation text
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(parsed_data, report_type)
            
            # Call Ollama API
            explanation = self._call_ollama(prompt)
            
            # Add disclaimer
            explanation_with_disclaimer = self._add_disclaimer(explanation)
            
            logger.info("Successfully generated explanation using Ollama")
            return explanation_with_disclaimer
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return self._get_fallback_explanation(parsed_data, report_type)
    
    def _build_prompt(self, parsed_data: Dict[str, Any], report_type: str) -> str:
        """Build the prompt for Ollama"""
        
        # Extract test results if available
        tests_info = ""
        if 'tests' in parsed_data and parsed_data['tests']:
            tests_info = "\n\nTest Results:\n"
            for test in parsed_data['tests']:
                tests_info += f"- {test.get('name', 'Unknown')}: {test.get('value', 'N/A')} {test.get('unit', '')}"
                tests_info += f" [Normal: {test.get('normal_range', 'N/A')}]"
                tests_info += f" - Status: {test.get('status', 'Unknown')}\n"
        
        # Build comprehensive prompt - simplified for better Meditron response
        prompt = f"""Explain these medical test results in simple, patient-friendly language:

{tests_info}

For each test:
1. What does this test measure?
2. Is the result normal or abnormal?
3. What does this mean for the patient's health?

Use simple language that an 8th grader can understand. Do not diagnose or recommend treatment."""

        return prompt
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate response"""
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            logger.info(f"Calling Ollama with model: {self.model_name}")
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                explanation = result.get('response', '').strip()
                
                if explanation:
                    logger.info("Successfully received response from Ollama")
                    return explanation
                else:
                    raise Exception("Empty response from Ollama")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout")
            raise Exception("AI service timeout - please try again")
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama service")
            raise Exception("AI service unavailable - is Ollama running?")
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
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
        """Test Ollama connection and return status"""
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                
                return {
                    "status": "connected",
                    "model": self.model_name,
                    "available_models": model_names,
                    "model_loaded": self.model_name in model_names
                }
            else:
                return {
                    "status": "error",
                    "message": "Ollama service responded with error"
                }
                
        except Exception as e:
            return {
                "status": "offline",
                "message": f"Cannot connect to Ollama: {str(e)}"
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
