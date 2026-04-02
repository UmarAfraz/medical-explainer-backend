"""
Report Parser Module for Medical Report Explanation System
Extracts structured data from blood test and imaging reports
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
from modules.utils import DataLoader, TextProcessor

logger = logging.getLogger(__name__)


class ReportParser:
    """Parse medical reports and extract structured data"""
    
    def __init__(self):
        """Initialize parser with reference data"""
        self.data_loader = DataLoader()
        self.text_processor = TextProcessor()
        self.reference_ranges = self.data_loader.load_reference_ranges()
    
    def parse_report(self, text: str, report_type: str = 'auto') -> Dict:
        """
        Main parsing function - routes to appropriate parser
        
        Args:
            text: Report text
            report_type: 'blood_test', 'imaging', or 'auto'
            
        Returns:
            Dictionary with parsed report data
        """
        # Clean text first
        text = self.text_processor.clean_text(text)
        
        # Route to appropriate parser
        if report_type == 'blood_test':
            return self.parse_blood_test(text)
        elif report_type == 'imaging':
            return self.parse_imaging_report(text)
        else:
            # Auto-detect (this should already be done by validator, but as fallback)
            if self._looks_like_blood_test(text):
                return self.parse_blood_test(text)
            else:
                return self.parse_imaging_report(text)
    
    def parse_blood_test(self, text: str) -> Dict:
        """
        Parse blood test report
        
        Args:
            text: Blood test report text
            
        Returns:
            Structured data dictionary
        """
        logger.info("Parsing blood test report")
        
        parsed_data = {
            'report_type': 'blood_test',
            'tests': [],
            'abnormal_flags': [],
            'summary': {}
        }
        
        # Extract test results
        tests = self._extract_test_values(text)
        
        for test in tests:
            test_name = test['test_name']
            value = test['value']
            unit = test['unit']
            
            # Get reference range from database
            reference = self.data_loader.get_test_reference(test_name)
            
            if reference:
                test['reference_min'] = reference.get('min_normal')
                test['reference_max'] = reference.get('max_normal')
                test['full_name'] = reference.get('full_name', test_name)
                test['description'] = reference.get('description', '')
                
                # Determine if value is normal
                if value is not None:
                    test['status'] = self._determine_status(
                        value, 
                        reference.get('min_normal'), 
                        reference.get('max_normal')
                    )
                    
                    # Add to abnormal flags if not normal
                    if test['status'] != 'normal':
                        parsed_data['abnormal_flags'].append({
                            'test': test_name,
                            'value': value,
                            'status': test['status']
                        })
            else:
                test['status'] = 'unknown'
                logger.warning(f"No reference range found for {test_name}")
            
            parsed_data['tests'].append(test)
        
        # Generate summary
        parsed_data['summary'] = {
            'total_tests': len(tests),
            'abnormal_count': len(parsed_data['abnormal_flags']),
            'test_categories': self._identify_test_categories(tests)
        }
        
        return parsed_data
    
    def _extract_test_values(self, text: str) -> List[Dict]:
        """
        Extract test names and values from blood test report
        
        Args:
            text: Report text
            
        Returns:
            List of test dictionaries
        """
        tests = []
        lines = text.split('\n')
        
        # Pattern to match test results
        # Examples:
        # "WBC: 7.5 × 10^9/L [4.0-11.0]"
        # "Glucose: 95 mg/dL (70-100)"
        # "Hemoglobin 14.5 g/dL 13.5-17.5"
        
        patterns = [
            # Pattern 1: Name: Value Unit [Range]
            r'([A-Za-z0-9_\s-]+?)[:\s]+(\d+\.?\d*)\s*([×x]?\s*\d+[\^]?\d*[/]?[A-Za-z]+)\s*[\[\(]?(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)[\]\)]?',
            # Pattern 2: Name Value Unit Range
            r'([A-Za-z0-9_\s-]+?)\s+(\d+\.?\d*)\s+([A-Za-z/%]+)\s+(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)',
            # Pattern 3: Simple Name: Value Unit
            r'([A-Za-z0-9_\s-]+?)[:\s]+(\d+\.?\d*)\s*([A-Za-z/%×x\^\d/]+)',
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try each pattern
            matched = False
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    
                    test_name = groups[0].strip()
                    # Normalize test name
                    test_name = self._normalize_test_name(test_name)
                    
                    try:
                        value = float(groups[1])
                    except:
                        value = None
                    
                    unit = groups[2].strip() if len(groups) > 2 else ''
                    
                    test_dict = {
                        'test_name': test_name,
                        'value': value,
                        'unit': unit,
                        'raw_line': line
                    }
                    
                    # Add reference range if captured
                    if len(groups) >= 5:
                        try:
                            test_dict['stated_min'] = float(groups[3])
                            test_dict['stated_max'] = float(groups[4])
                        except:
                            pass
                    
                    tests.append(test_dict)
                    matched = True
                    break
            
            # Also check for abnormal flags in the line
            if 'high' in line.lower() or 'low' in line.lower() or 'abnormal' in line.lower():
                logger.debug(f"Found abnormal flag in line: {line}")
        
        return tests
    
    def _normalize_test_name(self, name: str) -> str:
        """
        Normalize test name to match database
        
        Args:
            name: Raw test name
            
        Returns:
            Normalized test name
        """
        # Remove common prefixes/suffixes
        name = name.strip()
        name = re.sub(r'\s+\(.*?\)', '', name)  # Remove parenthetical
        name = name.replace(':', '').strip()
        
        # Common abbreviations mapping
        abbreviations = {
            'white blood cells': 'WBC',
            'red blood cells': 'RBC',
            'hemoglobin': 'HGB',
            'hematocrit': 'HCT',
            'platelets': 'PLT',
            'mean corpuscular volume': 'MCV',
            'glucose': 'Glucose',
            'cholesterol': 'Total_Cholesterol',
            'ldl': 'LDL',
            'hdl': 'HDL',
            'triglycerides': 'Triglycerides',
        }
        
        name_lower = name.lower()
        for full_name, abbrev in abbreviations.items():
            if full_name in name_lower:
                return abbrev
        
        # If it's already an abbreviation, use as is
        if len(name) <= 10 and name.replace('_', '').replace('-', '').isalnum():
            return name.upper() if len(name) <= 5 else name
        
        return name
    
    def _determine_status(self, value: float, min_normal: float, 
                         max_normal: float) -> str:
        """
        Determine if value is normal, high, or low
        
        Args:
            value: Test value
            min_normal: Minimum normal value
            max_normal: Maximum normal value
            
        Returns:
            'normal', 'high', or 'low'
        """
        if value is None or min_normal is None or max_normal is None:
            return 'unknown'
        
        if value < min_normal:
            return 'low'
        elif value > max_normal:
            return 'high'
        else:
            return 'normal'
    
    def _identify_test_categories(self, tests: List[Dict]) -> List[str]:
        """
        Identify what categories of tests are present
        
        Args:
            tests: List of test dictionaries
            
        Returns:
            List of category names
        """
        categories = set()
        
        for test in tests:
            # Check against reference data
            test_name = test['test_name']
            df = self.reference_ranges
            result = df[df['test_name'] == test_name]
            
            if not result.empty:
                category = result.iloc[0]['category']
                categories.add(category)
        
        return list(categories)
    
    def _looks_like_blood_test(self, text: str) -> bool:
        """
        Check if text looks like a blood test report
        
        Args:
            text: Report text
            
        Returns:
            True if appears to be blood test
        """
        blood_test_keywords = [
            'cbc', 'complete blood count', 'wbc', 'rbc', 'hemoglobin',
            'glucose', 'cholesterol', 'lipid panel', 'metabolic panel'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in blood_test_keywords)
    
    def parse_imaging_report(self, text: str) -> Dict:
        """
        Parse imaging report (X-ray, CT, MRI, etc.)
        
        Args:
            text: Imaging report text
            
        Returns:
            Structured data dictionary
        """
        logger.info("Parsing imaging report")
        
        # Define section keywords
        section_keywords = [
            'CLINICAL INDICATION', 'INDICATION',
            'TECHNIQUE', 'COMPARISON',
            'FINDINGS', 'IMPRESSION',
            'RECOMMENDATION', 'CONCLUSION'
        ]
        
        # Extract sections
        sections = self.text_processor.extract_sections(text, section_keywords)
        
        parsed_data = {
            'report_type': 'imaging',
            'sections': sections,
            'key_findings': [],
            'impression': sections.get('impression', sections.get('conclusion', '')),
            'modality': self._detect_imaging_modality(text)
        }
        
        # Extract key findings
        findings_text = sections.get('findings', '')
        if findings_text:
            parsed_data['key_findings'] = self._extract_imaging_findings(findings_text)
        
        # Check for abnormalities
        parsed_data['has_abnormalities'] = self._check_for_abnormalities(text)
        
        return parsed_data
    
    def _detect_imaging_modality(self, text: str) -> str:
        """
        Detect type of imaging study
        
        Args:
            text: Report text
            
        Returns:
            Modality name (X-ray, CT, MRI, etc.)
        """
        text_lower = text.lower()
        
        modalities = {
            'x-ray': ['x-ray', 'radiograph', 'plain film'],
            'ct': ['ct scan', 'computed tomography', 'ct '],
            'mri': ['mri', 'magnetic resonance'],
            'ultrasound': ['ultrasound', 'sonogram', 'sonography'],
            'mammogram': ['mammogram', 'mammography'],
            'pet': ['pet scan', 'positron emission'],
            'nuclear': ['nuclear medicine', 'bone scan']
        }
        
        for modality, keywords in modalities.items():
            if any(keyword in text_lower for keyword in keywords):
                return modality.upper()
        
        return 'Unknown'
    
    def _extract_imaging_findings(self, findings_text: str) -> List[str]:
        """
        Extract key findings from findings section
        
        Args:
            findings_text: Findings section text
            
        Returns:
            List of finding statements
        """
        # Split by sentences
        sentences = re.split(r'[.!?]+', findings_text)
        
        key_findings = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short fragments
                continue
            
            # Look for significant findings
            significant_terms = [
                'mass', 'lesion', 'nodule', 'opacity', 'consolidation',
                'effusion', 'pneumothorax', 'fracture', 'hemorrhage',
                'abnormal', 'enlarged', 'thickening'
            ]
            
            if any(term in sentence.lower() for term in significant_terms):
                key_findings.append(sentence)
        
        return key_findings
    
    def _check_for_abnormalities(self, text: str) -> bool:
        """
        Check if report mentions abnormalities
        
        Args:
            text: Full report text
            
        Returns:
            True if abnormalities detected
        """
        text_lower = text.lower()
        
        # Normal indicators
        normal_phrases = [
            'no acute', 'within normal', 'unremarkable',
            'negative for', 'no evidence of'
        ]
        
        # Abnormal indicators
        abnormal_phrases = [
            'abnormal', 'concerning', 'suspicious',
            'mass', 'lesion', 'fracture', 'effusion'
        ]
        
        normal_count = sum(1 for phrase in normal_phrases if phrase in text_lower)
        abnormal_count = sum(1 for phrase in abnormal_phrases if phrase in text_lower)
        
        return abnormal_count > normal_count


# Example usage and testing
if __name__ == "__main__":
    parser = ReportParser()
    
    # Test with sample blood test
    sample_blood = """
    Complete Blood Count (CBC)
    White Blood Cells (WBC): 7.5 × 10^9/L [4.0-11.0]
    Hemoglobin (HGB): 14.5 g/dL [13.5-17.5]
    Glucose: 195 mg/dL [70-100] HIGH
    """
    
    result = parser.parse_blood_test(sample_blood)
    print("Blood Test Parse Result:")
    print(f"Found {len(result['tests'])} tests")
    print(f"Abnormal tests: {len(result['abnormal_flags'])}")
    
    # Test with sample imaging
    sample_imaging = """
    CHEST X-RAY
    
    FINDINGS:
    The lungs are clear. No consolidation or effusion.
    Heart size is normal.
    
    IMPRESSION:
    No acute cardiopulmonary process.
    """
    
    result = parser.parse_imaging_report(sample_imaging)
    print("\nImaging Parse Result:")
    print(f"Modality: {result['modality']}")
    print(f"Has abnormalities: {result['has_abnormalities']}")
