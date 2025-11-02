"""
Automation Form Data Model
Represents the recommendation and advice stage form after fact finding
Form ID: 124
"""
from typing import Dict, Optional, Any, List
from datetime import datetime
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from field_mapper import FieldMapper


class AutomationForm:
    """
    Model for the Insurance Automation Form (recommendation stage)
    This form follows the fact find and contains provider recommendations
    """

    def __init__(self, config_path: str = "config/automation_form_mappings.yaml"):
        """Initialize an automation form with all sections

        Args:
            config_path: Path to automation form field mappings
        """
        # Client details
        self.client_details: Dict[str, Any] = {}

        # Scope and limitations
        self.scope_of_advice: Dict[str, Any] = {}
        self.limitations: Dict[str, Any] = {}

        # Existing cover details
        self.main_existing_cover: Dict[str, Any] = {}
        self.partner_existing_cover: Dict[str, Any] = {}

        # Recommendations
        self.recommendation: Dict[str, Any] = {}
        self.additional: Dict[str, Any] = {}

        # Raw data storage
        self._raw_data: Dict[str, Any] = {}

        # Initialize field mapper
        self.field_mapper = None
        try:
            self.field_mapper = FieldMapper(config_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Automation form mappings not found at {config_path}")

    def load_from_dict(self, data: Dict[str, Any]):
        """
        Load automation form data from a dictionary

        Args:
            data: Dictionary containing form fields (typically from Gravity Forms)
        """
        self._raw_data = data.copy()

        if not self.field_mapper:
            raise RuntimeError("Field mapper not initialized")

        # Extract all categories
        all_data = self.field_mapper.extract_all(data)

        # Process client details
        self.client_details = all_data.get('client_details', {})

        # Process scope of advice
        self.scope_of_advice = all_data.get('scope_of_advice', {})
        self._process_checkbox_fields(self.scope_of_advice)

        # Process limitations
        self.limitations = all_data.get('limitations', {})
        self._process_checkbox_fields(self.limitations)

        # Process existing cover for main contact
        self.main_existing_cover = all_data.get('main_existing_cover', {})
        self._parse_insurance_amounts(self.main_existing_cover)

        # Process existing cover for partner (if couple)
        if self.is_couple():
            self.partner_existing_cover = all_data.get('partner_existing_cover', {})
            self._parse_insurance_amounts(self.partner_existing_cover)
        else:
            self.partner_existing_cover = {}

        # Process recommendations
        self.recommendation = all_data.get('recommendation', {})
        self._parse_quote_amounts(self.recommendation)

        # Process additional fields
        self.additional = all_data.get('additional', {})
        if not self.additional.get('recommendation_date'):
            self.additional['recommendation_date'] = datetime.now().isoformat()

        return self

    def load_from_json(self, json_path: str):
        """
        Load automation form data from a JSON file

        Args:
            json_path: Path to JSON file containing form data
        """
        with open(json_path, 'r') as f:
            data = json.load(f)
        return self.load_from_dict(data)

    def _process_checkbox_fields(self, section_data: Dict[str, Any]):
        """
        Process checkbox fields to boolean values

        Args:
            section_data: Section containing checkbox fields
        """
        for key, value in section_data.items():
            if isinstance(value, str):
                # Convert Yes/No, True/False strings to boolean
                if value.lower() in ['yes', 'true', '1', 'checked']:
                    section_data[key] = True
                elif value.lower() in ['no', 'false', '0', 'unchecked', '']:
                    section_data[key] = False

    def _parse_insurance_amounts(self, insurance_data: Dict[str, Any]):
        """
        Parse insurance amounts and premiums to float values

        Args:
            insurance_data: Dictionary containing insurance fields
        """
        currency_fields = ['life_amount', 'tpd_amount', 'trauma_amount',
                          'income_protection_amount', 'medical_amount',
                          'existing_premiums']

        for field in currency_fields:
            if field in insurance_data:
                insurance_data[field] = self._parse_currency(insurance_data[field])

    def _parse_quote_amounts(self, quote_data: Dict[str, Any]):
        """
        Parse quote amounts from providers

        Args:
            quote_data: Dictionary containing quote fields
        """
        quote_fields = ['quote_partners_life', 'quote_fidelity_life',
                       'quote_aia', 'quote_asteron', 'quote_chubb', 'quote_nib']

        for field in quote_fields:
            if field in quote_data:
                quote_data[field] = self._parse_currency(quote_data[field])

    def _parse_currency(self, value: Any) -> Optional[float]:
        """
        Parse currency string to float, handling various formats

        Args:
            value: String or number representing currency

        Returns:
            Float value or None if parsing fails
        """
        if value is None or value == '':
            return None

        # If already a number, return it
        if isinstance(value, (int, float)):
            return float(value)

        # Convert to string and clean
        value_str = str(value)
        # Remove currency symbols and commas
        value_str = value_str.replace('$', '').replace(',', '').strip()

        try:
            return float(value_str)
        except ValueError:
            return None

    def is_couple(self) -> bool:
        """Check if this is advice for a couple"""
        is_couple = self.client_details.get('is_couple')
        if isinstance(is_couple, bool):
            return is_couple
        if isinstance(is_couple, str):
            return is_couple.lower() in ['yes', 'true', 'couple', '1']
        return False

    def get_selected_scope(self) -> List[str]:
        """Get list of insurance types included in scope"""
        scope_types = []
        scope_mapping = {
            'life_insurance': 'Life Insurance',
            'income_protection': 'Income Protection',
            'trauma_cover': 'Trauma Cover',
            'health_insurance': 'Health Insurance',
            'total_permanent_disability': 'Total & Permanent Disability',
            'acc': 'ACC'
        }

        for key, display_name in scope_mapping.items():
            if self.scope_of_advice.get(key):
                scope_types.append(display_name)

        return scope_types

    def get_limitation_reasons(self) -> List[str]:
        """Get list of reasons for limiting scope"""
        reasons = []
        reason_mapping = {
            'employer_medical': 'Medical cover through employer',
            'no_debt_strong_assets': 'No debt and strong asset base',
            'budget_limitations': 'Budget limitations',
            'self_insure': 'Can self-insure the risk',
            'no_dependants': 'No dependants',
            'uninsurable_occupation': 'Uninsurable occupation',
            'other': 'Other reasons'
        }

        for key, display_text in reason_mapping.items():
            if self.limitations.get(key):
                reasons.append(display_text)

        return reasons

    def get_recommended_provider(self) -> Optional[str]:
        """Get the selected/recommended provider"""
        return self.recommendation.get('selected_provider')

    def get_lowest_quote(self) -> tuple[Optional[str], Optional[float]]:
        """Get the provider with the lowest quote"""
        quotes = {
            'Partners Life': self.recommendation.get('quote_partners_life'),
            'Fidelity Life': self.recommendation.get('quote_fidelity_life'),
            'AIA': self.recommendation.get('quote_aia'),
            'Asteron': self.recommendation.get('quote_asteron'),
            'Chubb': self.recommendation.get('quote_chubb'),
            'nib': self.recommendation.get('quote_nib')
        }

        # Filter out None values
        valid_quotes = {k: v for k, v in quotes.items() if v is not None}

        if not valid_quotes:
            return None, None

        # Find minimum quote
        min_provider = min(valid_quotes, key=valid_quotes.get)
        return min_provider, valid_quotes[min_provider]

    def to_dict(self) -> Dict[str, Any]:
        """Convert automation form to dictionary for serialization"""
        return {
            'client_details': self.client_details,
            'scope_of_advice': self.scope_of_advice,
            'limitations': self.limitations,
            'main_existing_cover': self.main_existing_cover,
            'partner_existing_cover': self.partner_existing_cover,
            'recommendation': self.recommendation,
            'additional': self.additional,
            'is_couple': self.is_couple(),
            'selected_scope': self.get_selected_scope(),
            'limitation_reasons': self.get_limitation_reasons()
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert automation form to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def __str__(self) -> str:
        """String representation of automation form"""
        email = self.client_details.get('email', 'Unknown')
        provider = self.get_recommended_provider() or 'No provider selected'
        return f"AutomationForm(email={email}, provider={provider}, is_couple={self.is_couple()})"

    def __repr__(self) -> str:
        """Detailed representation of automation form"""
        return f"AutomationForm({self.to_dict()})"