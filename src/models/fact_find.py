"""
Fact Find Data Models
Represents the structure of fact find forms for insurance applications
"""
from typing import Dict, Optional, Any
from datetime import datetime
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from field_mapper import FieldMapper


class FactFind:
    """
    Main class to represent a complete fact find form
    """

    def __init__(self, use_field_mapper: bool = True, config_path: str = "config/field_mappings.yaml"):
        """Initialize an empty fact find with all sections

        Args:
            use_field_mapper: Whether to use the FieldMapper for data extraction
            config_path: Path to field mappings configuration file
        """
        # Core information sections
        self.client_info: Dict[str, Any] = {}
        self.partner_info: Optional[Dict[str, Any]] = None
        self.case_info: Dict[str, Any] = {}

        # Employment sections
        self.employment_main: Dict[str, Any] = {}
        self.employment_partner: Optional[Dict[str, Any]] = None

        # Financial sections
        self.financial_info: Dict[str, Any] = {}  # Legacy support
        self.household_info: Dict[str, Any] = {}
        self.assets: Dict[str, Any] = {}
        self.liabilities: Dict[str, Any] = {}
        self.investment_properties: Dict[str, Any] = {}
        self.kiwisaver: Dict[str, Any] = {}

        # Insurance sections
        self.existing_insurance: Dict[str, Any] = {}  # Legacy combined
        self.existing_insurance_main: Dict[str, Any] = {}
        self.existing_insurance_partner: Dict[str, Any] = {}

        # Health and medical sections
        self.health_info: Dict[str, Any] = {}  # Legacy support
        self.medical_main: Dict[str, Any] = {}
        self.medical_partner: Dict[str, Any] = {}

        # Family and recreational
        self.children: Dict[str, Any] = {}
        self.recreational: Dict[str, Any] = {}

        # Needs analysis sections
        self.needs_life_main: Dict[str, Any] = {}
        self.needs_life_partner: Dict[str, Any] = {}
        self.needs_trauma_main: Dict[str, Any] = {}
        self.needs_trauma_partner: Dict[str, Any] = {}
        self.needs_income_main: Dict[str, Any] = {}
        self.needs_income_partner: Dict[str, Any] = {}
        self.needs_accident: Dict[str, Any] = {}
        self.needs_medical_main: Dict[str, Any] = {}
        self.needs_medical_partner: Dict[str, Any] = {}

        # Scope of advice
        self.scope_of_advice: Dict[str, Any] = {}

        # Raw data storage
        self._raw_data: Dict[str, Any] = {}

        # Initialize field mapper if requested
        self.field_mapper = None
        if use_field_mapper:
            try:
                self.field_mapper = FieldMapper(config_path)
            except FileNotFoundError:
                # Fall back to legacy mode if config not found
                pass

    def load_from_dict(self, data: Dict[str, Any]):
        """
        Load fact find data from a dictionary (typically from JSON)

        Args:
            data: Dictionary containing fact find fields
        """
        self._raw_data = data.copy()

        if self.field_mapper:
            # Use field mapper for extraction
            self._load_with_mapper(data)
        else:
            # Fall back to legacy extraction
            self._load_legacy(data)

        return self

    def _load_with_mapper(self, data: Dict[str, Any]):
        """Load data using the field mapper"""
        # Extract all categories
        all_data = self.field_mapper.extract_all(data)

        # Map extracted data to instance attributes
        self.case_info = all_data.get('admin', {})
        if not self.case_info.get('form_date'):
            self.case_info['form_date'] = datetime.now().isoformat()

        # Process client information
        self.client_info = all_data.get('client', {})
        if 'annual_income' in self.client_info:
            self.client_info['annual_income'] = self._parse_currency(self.client_info['annual_income'])

        # Process partner information
        partner_data = all_data.get('partner', {})
        if partner_data and any(partner_data.values()):
            self.partner_info = partner_data
            if 'annual_income' in self.partner_info:
                self.partner_info['annual_income'] = self._parse_currency(self.partner_info['annual_income'])
        else:
            self.partner_info = None

        # Process employment information
        self.employment_main = all_data.get('employment_main', {})
        self._parse_employment_section(self.employment_main)

        employment_partner_data = all_data.get('employment_partner', {})
        if employment_partner_data and any(employment_partner_data.values()):
            self.employment_partner = employment_partner_data
            self._parse_employment_section(self.employment_partner)
        else:
            self.employment_partner = None

        # Process household information
        self.household_info = all_data.get('household', {})
        self._parse_household_section(self.household_info)

        # Process assets
        self.assets = all_data.get('assets', {})
        self._parse_assets_section(self.assets)

        # Process liabilities
        self.liabilities = all_data.get('liabilities', {})
        for key in self.liabilities:
            if 'value' in key:
                self.liabilities[key] = self._parse_currency(self.liabilities[key])

        # Process investment properties
        self.investment_properties = all_data.get('investment_properties', {})
        self._parse_investment_properties(self.investment_properties)

        # Process KiwiSaver
        self.kiwisaver = all_data.get('kiwisaver', {})
        for key in self.kiwisaver:
            if 'balance' in key:
                self.kiwisaver[key] = self._parse_currency(self.kiwisaver[key])

        # Process existing insurance
        self.existing_insurance_main = all_data.get('existing_insurance_main', {})
        self._parse_insurance_section(self.existing_insurance_main)

        self.existing_insurance_partner = all_data.get('existing_insurance_partner', {})
        self._parse_insurance_section(self.existing_insurance_partner)

        # Legacy combined insurance
        self.existing_insurance = {**self.existing_insurance_main, **self.existing_insurance_partner}

        # Process medical information
        self.medical_main = all_data.get('medical_main', {})
        self.medical_partner = all_data.get('medical_partner', {})

        # Legacy health_info for backward compatibility
        self.health_info = {**self.medical_main, **self.medical_partner}

        # Process children information
        self.children = all_data.get('children', {})

        # Process recreational information
        self.recreational = all_data.get('recreational', {})

        # Process all needs analysis sections
        self.needs_life_main = all_data.get('needs_life_main', {})
        self._parse_needs_section(self.needs_life_main)

        self.needs_life_partner = all_data.get('needs_life_partner', {})
        self._parse_needs_section(self.needs_life_partner)

        self.needs_trauma_main = all_data.get('needs_trauma_main', {})
        self._parse_needs_section(self.needs_trauma_main)

        self.needs_trauma_partner = all_data.get('needs_trauma_partner', {})
        self._parse_needs_section(self.needs_trauma_partner)

        self.needs_income_main = all_data.get('needs_income_main', {})
        self._parse_needs_section(self.needs_income_main)

        self.needs_income_partner = all_data.get('needs_income_partner', {})
        self._parse_needs_section(self.needs_income_partner)

        self.needs_accident = all_data.get('needs_accident', {})

        self.needs_medical_main = all_data.get('needs_medical_main', {})
        self._parse_needs_section(self.needs_medical_main)

        self.needs_medical_partner = all_data.get('needs_medical_partner', {})
        self._parse_needs_section(self.needs_medical_partner)

        # Process scope of advice
        self.scope_of_advice = all_data.get('scope_of_advice', {})

        # Legacy financial_info for backward compatibility
        self.financial_info = {
            'mortgage': self.household_info.get('current_mortgage') or self.liabilities.get('mortgage'),
            'home_value': self.household_info.get('current_house_value')
        }

    def _parse_employment_section(self, employment_data: Dict[str, Any]):
        """Parse employment section, converting currency fields"""
        if not employment_data:
            return

        currency_fields = ['annual_income', 'commissions_bonuses', 'unearned_income', 'business_debt']
        for field in currency_fields:
            if field in employment_data:
                employment_data[field] = self._parse_currency(employment_data[field])

    def _parse_household_section(self, household_data: Dict[str, Any]):
        """Parse household section, converting currency fields"""
        if not household_data:
            return

        currency_fields = ['current_house_value', 'current_mortgage', 'monthly_mortgage_repayments', 'weekly_rent']
        for field in currency_fields:
            if field in household_data:
                household_data[field] = self._parse_currency(household_data[field])

    def _parse_assets_section(self, assets_data: Dict[str, Any]):
        """Parse assets section, converting all value fields"""
        if not assets_data:
            return

        for key in assets_data:
            if 'value' in key or 'total' in key:
                assets_data[key] = self._parse_currency(assets_data[key])

    def _parse_investment_properties(self, properties_data: Dict[str, Any]):
        """Parse investment properties, converting currency fields"""
        if not properties_data:
            return

        for key in properties_data:
            if any(term in key for term in ['value', 'mortgage', 'rent', 'total', 'debt', 'equity']):
                properties_data[key] = self._parse_currency(properties_data[key])

    def _parse_insurance_section(self, insurance_data: Dict[str, Any]):
        """Parse insurance section, converting currency fields"""
        if not insurance_data:
            return

        for key in insurance_data:
            if any(term in key for term in ['amount', 'premium', 'excess']):
                insurance_data[key] = self._parse_currency(insurance_data[key])

    def _parse_needs_section(self, needs_data: Dict[str, Any]):
        """Parse needs analysis section, converting currency fields"""
        if not needs_data:
            return

        for key in needs_data:
            # Most needs fields are currency except some specific ones
            if key not in ['needs_analysis_notes', 'income_type', 'loe_mrc_type', 'acc_offsets',
                          'wait_period_weeks', 'claim_period_years', 'leave_entitlements_weeks',
                          'buyback_option', 'tpd_addon']:
                if isinstance(needs_data[key], str) and needs_data[key]:
                    needs_data[key] = self._parse_currency(needs_data[key])

    def _load_legacy(self, data: Dict[str, Any]):
        """Legacy loading method for backward compatibility"""
        # Extract case information
        self.case_info = {
            'case_id': data.get('f516'),
            'form_date': datetime.now().isoformat()
        }

        # Extract client information
        self.client_info = {
            'first_name': data.get('f144'),
            'last_name': data.get('f145'),
            'email': data.get('f219'),
            'date_of_birth': data.get('f94'),
            'occupation': data.get('f6'),
            'annual_income': self._parse_currency(data.get('f10'))
        }

        # Extract financial information
        self.financial_info = {
            'mortgage': self._parse_currency(data.get('f15')),
            'home_value': self._parse_currency(data.get('f16'))
        }

        # Partner info would be populated if present
        # For now, leaving as None if not a couple

    def load_from_json(self, json_path: str):
        """
        Load fact find data from a JSON file

        Args:
            json_path: Path to JSON file containing fact find data
        """
        with open(json_path, 'r') as f:
            data = json.load(f)
        return self.load_from_dict(data)

    def _parse_currency(self, value: Any) -> Optional[float]:
        """
        Parse currency string to float, handling various formats

        Args:
            value: String or number representing currency

        Returns:
            Float value or None if parsing fails
        """
        if value is None:
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

    def get_client_full_name(self) -> str:
        """Get the client's full name"""
        first = self.client_info.get('first_name', '')
        last = self.client_info.get('last_name', '')
        return f"{first} {last}".strip()

    def get_partner_full_name(self) -> Optional[str]:
        """Get the partner's full name if exists"""
        if not self.partner_info:
            return None
        first = self.partner_info.get('first_name', '')
        last = self.partner_info.get('last_name', '')
        return f"{first} {last}".strip() if first or last else None

    def is_couple(self) -> bool:
        """Check if this is a couple or single application"""
        return self.partner_info is not None and len(self.partner_info) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert fact find to dictionary for serialization"""
        return {
            # Core information
            'case_info': self.case_info,
            'client_info': self.client_info,
            'partner_info': self.partner_info,

            # Employment
            'employment_main': self.employment_main,
            'employment_partner': self.employment_partner,

            # Financial and property
            'household_info': self.household_info,
            'assets': self.assets,
            'liabilities': self.liabilities,
            'investment_properties': self.investment_properties,
            'kiwisaver': self.kiwisaver,

            # Insurance
            'existing_insurance_main': self.existing_insurance_main,
            'existing_insurance_partner': self.existing_insurance_partner,

            # Medical and health
            'medical_main': self.medical_main,
            'medical_partner': self.medical_partner,

            # Family and lifestyle
            'children': self.children,
            'recreational': self.recreational,

            # Needs analysis
            'needs_life_main': self.needs_life_main,
            'needs_life_partner': self.needs_life_partner,
            'needs_trauma_main': self.needs_trauma_main,
            'needs_trauma_partner': self.needs_trauma_partner,
            'needs_income_main': self.needs_income_main,
            'needs_income_partner': self.needs_income_partner,
            'needs_accident': self.needs_accident,
            'needs_medical_main': self.needs_medical_main,
            'needs_medical_partner': self.needs_medical_partner,

            # Scope of advice
            'scope_of_advice': self.scope_of_advice,

            # Legacy support
            'financial_info': self.financial_info,
            'existing_insurance': self.existing_insurance,
            'health_info': self.health_info,

            # Metadata
            'is_couple': self.is_couple()
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert fact find to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def __str__(self) -> str:
        """String representation of fact find"""
        case_id = self.case_info.get('case_id', 'Unknown')
        client_name = self.get_client_full_name() or 'Unknown Client'
        return f"FactFind(case_id={case_id}, client={client_name}, is_couple={self.is_couple()})"

    def __repr__(self) -> str:
        """Detailed representation of fact find"""
        return f"FactFind({self.to_dict()})"