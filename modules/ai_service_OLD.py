"""
AI Service Module for Medical Report Explanation System
Integrates with OpenAI GPT-4 to generate patient-friendly explanations
"""

import logging
import json
from typing import Dict, List, Optional
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class AIExplainer:
    """Generate patient-friendly medical explanations using AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI service
        
        Args:
            api_key: OpenAI API key (uses Config if not provided)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.temperature = Config.OPENAI_TEMPERATURE
    
    def generate_explanation(self, parsed_data: Dict) -> str:
        """
        Generate explanation based on parsed report data
        
        Args:
            parsed_data: Structured data from parser
            
        Returns:
            Patient-friendly explanation text
        """
        report_type = parsed_data.get('report_type', 'unknown')
        
        if report_type == 'blood_test':
            return self._explain_blood_test(parsed_data)
        elif report_type == 'imaging':
            return self._explain_imaging_report(parsed_data)
        else:
            return self._generate_generic_explanation(parsed_data)
    
    def _explain_blood_test(self, parsed_data: Dict) -> str:
        """
        Generate explanation for blood test results
        
        Args:
            parsed_data: Parsed blood test data
            
        Returns:
            Explanation text
        """
        logger.info("Generating blood test explanation")
        
        # Build the prompt
        prompt = self._build_blood_test_prompt(parsed_data)
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            explanation = response.choices[0].message.content
            logger.info("Successfully generated blood test explanation")
            return explanation
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._generate_fallback_explanation(parsed_data)
    
    def _explain_imaging_report(self, parsed_data: Dict) -> str:
        """
        Generate explanation for imaging report
        
        Args:
            parsed_data: Parsed imaging data
            
        Returns:
            Explanation text
        """
        logger.info("Generating imaging report explanation")
        
        # Build the prompt
        prompt = self._build_imaging_prompt(parsed_data)
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            explanation = response.choices[0].message.content
            logger.info("Successfully generated imaging explanation")
            return explanation
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._generate_fallback_explanation(parsed_data)
    
    def _get_system_prompt(self) -> str:
        """
        Get system prompt that defines AI behavior
        
        Returns:
            System prompt text
        """
        return """You are a medical communication assistant helping patients understand their medical reports. 

YOUR ROLE:
- Translate complex medical terminology into simple, patient-friendly language
- Explain what tests measure and what results mean
- Provide general health context without diagnosing

CRITICAL CONSTRAINTS (YOU MUST FOLLOW THESE):
1. NEVER provide diagnosis - you are NOT diagnosing conditions
2. NEVER recommend specific treatments or medications
3. NEVER suggest the patient has a specific disease or condition
4. ALWAYS use simple language (8th-grade reading level)
5. ALWAYS encourage consulting with healthcare provider
6. ALWAYS be clear this is educational, not medical advice

STYLE GUIDELINES:
- Use short sentences and simple words
- Avoid medical jargon when possible
- When using medical terms, immediately explain them in plain language
- Be reassuring but accurate
- Focus on what the tests measure, not what diseases they indicate

FORMAT YOUR RESPONSE AS:
1. Brief overview of what was tested
2. Explanation of each result in simple terms
3. General context about what abnormal values might mean (WITHOUT diagnosing)
4. Clear guidance to discuss with doctor

Remember: Your goal is to help patients UNDERSTAND their reports, not to replace their doctor."""
    
    def _build_blood_test_prompt(self, parsed_data: Dict) -> str:
        """
        Build prompt for blood test explanation
        
        Args:
            parsed_data: Parsed blood test data
            
        Returns:
            Prompt text
        """
        tests = parsed_data.get('tests', [])
        abnormal_flags = parsed_data.get('abnormal_flags', [])
        
        prompt = "Please explain the following blood test results to a patient in simple, easy-to-understand language:\n\n"
        
        # Add test results
        for test in tests:
            test_name = test.get('full_name', test.get('test_name', 'Unknown'))
            value = test.get('value')
            unit = test.get('unit', '')
            status = test.get('status', 'unknown')
            description = test.get('description', '')
            ref_min = test.get('reference_min')
            ref_max = test.get('reference_max')
            
            prompt += f"\nTest: {test_name}\n"
            if description:
                prompt += f"What it measures: {description}\n"
            prompt += f"Your result: {value} {unit}\n"
            if ref_min and ref_max:
                prompt += f"Normal range: {ref_min}-{ref_max} {unit}\n"
            prompt += f"Status: {status}\n"
        
        # Highlight abnormal results
        if abnormal_flags:
            prompt += f"\n\nNote: {len(abnormal_flags)} result(s) are outside normal range:\n"
            for flag in abnormal_flags:
                prompt += f"- {flag['test']}: {flag['status']}\n"
        
        prompt += "\n\nPlease provide a clear, patient-friendly explanation that:"
        prompt += "\n1. Explains what each test measures in simple terms"
        prompt += "\n2. Indicates which results are normal and which are not"
        prompt += "\n3. Provides general context about what abnormal values typically mean (without diagnosing)"
        prompt += "\n4. Ends with encouragement to discuss results with their healthcare provider"
        
        return prompt
    
    def _build_imaging_prompt(self, parsed_data: Dict) -> str:
        """
        Build prompt for imaging report explanation
        
        Args:
            parsed_data: Parsed imaging data
            
        Returns:
            Prompt text
        """
        modality = parsed_data.get('modality', 'Imaging')
        sections = parsed_data.get('sections', {})
        impression = parsed_data.get('impression', '')
        key_findings = parsed_data.get('key_findings', [])
        has_abnormalities = parsed_data.get('has_abnormalities', False)
        
        prompt = f"Please explain the following {modality} report to a patient in simple, easy-to-understand language:\n\n"
        
        # Add indication if present
        if 'indication' in sections:
            prompt += f"Why the test was done: {sections['indication']}\n\n"
        
        # Add findings
        if 'findings' in sections:
            prompt += f"What the radiologist saw:\n{sections['findings']}\n\n"
        
        # Add impression/conclusion
        if impression:
            prompt += f"Radiologist's summary:\n{impression}\n\n"
        
        # Add key findings if extracted
        if key_findings:
            prompt += "Key points from the report:\n"
            for finding in key_findings:
                prompt += f"- {finding}\n"
            prompt += "\n"
        
        prompt += "Please provide a clear, patient-friendly explanation that:"
        prompt += "\n1. Explains what this imaging test looks at"
        prompt += "\n2. Translates medical terminology into everyday language"
        prompt += "\n3. Explains the main findings in simple terms"
        
        if has_abnormalities:
            prompt += "\n4. Provides context about the findings WITHOUT diagnosing"
        else:
            prompt += "\n4. Reassures if no significant issues were found"
        
        prompt += "\n5. Encourages discussion with healthcare provider"
        
        return prompt
    
    def _generate_generic_explanation(self, parsed_data: Dict) -> str:
        """
        Generate generic explanation when report type is unknown
        
        Args:
            parsed_data: Parsed data
            
        Returns:
            Generic explanation
        """
        return """I've reviewed your medical report, but I need more specific information to provide a detailed explanation.

I can help explain:
- Blood test results (CBC, metabolic panels, lipid panels, etc.)
- Imaging reports (X-rays, CT scans, MRIs, ultrasounds)

Please ensure your report includes:
- Test names and values
- Reference ranges
- Or imaging findings and impressions

For the best explanation, please provide a complete medical report."""
    
    def _generate_fallback_explanation(self, parsed_data: Dict) -> str:
        """
        Generate fallback explanation if API call fails
        
        Args:
            parsed_data: Parsed data
            
        Returns:
            Basic explanation without AI
        """
        logger.warning("Using fallback explanation due to API error")
        
        report_type = parsed_data.get('report_type', 'unknown')
        
        if report_type == 'blood_test':
            tests = parsed_data.get('tests', [])
            abnormal_count = len(parsed_data.get('abnormal_flags', []))
            
            explanation = "# Your Blood Test Results\n\n"
            explanation += f"Your report includes {len(tests)} test(s).\n\n"
            
            for test in tests:
                test_name = test.get('full_name', test.get('test_name'))
                value = test.get('value')
                unit = test.get('unit')
                status = test.get('status')
                
                explanation += f"**{test_name}**: {value} {unit} - {status.upper()}\n"
            
            if abnormal_count > 0:
                explanation += f"\n{abnormal_count} result(s) are outside the normal range. "
                explanation += "Please discuss these with your healthcare provider.\n"
            
            return explanation
        
        else:
            return "Unable to generate detailed explanation at this time. Please consult with your healthcare provider to discuss your results."
    
    def test_api_connection(self) -> bool:
        """
        Test if API connection is working
        
        Returns:
            True if connection successful
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            logger.info("API connection test successful")
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # This will only work if you have API key set
    try:
        explainer = AIExplainer()
        
        # Test API connection
        if explainer.test_api_connection():
            print("✓ OpenAI API connection successful")
        else:
            print("✗ OpenAI API connection failed")
        
        # Test with sample data
        sample_data = {
            'report_type': 'blood_test',
            'tests': [
                {
                    'test_name': 'WBC',
                    'full_name': 'White Blood Cells',
                    'value': 7.5,
                    'unit': '10^9/L',
                    'status': 'normal',
                    'reference_min': 4.0,
                    'reference_max': 11.0,
                    'description': 'Cells that fight infection'
                }
            ],
            'abnormal_flags': []
        }
        
        explanation = explainer.generate_explanation(sample_data)
        print("\nGenerated explanation:")
        print(explanation)
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set OPENAI_API_KEY in your environment")
