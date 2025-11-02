"""
Insurance Workflow Processor
Handles the complete insurance advisory workflow combining fact find and automation forms
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.fact_find import FactFind
from models.automation_form import AutomationForm


class InsuranceWorkflow:
    """
    Manages the complete insurance advisory workflow
    Combines fact find data with recommendation/automation data
    """

    def __init__(self):
        """Initialize the insurance workflow processor"""
        self.fact_find: Optional[FactFind] = None
        self.automation_form: Optional[AutomationForm] = None
        self.workflow_data: Dict[str, Any] = {}

    def load_fact_find(self, data: Dict[str, Any]) -> 'InsuranceWorkflow':
        """
        Load fact find form data

        Args:
            data: Fact find form data dictionary

        Returns:
            Self for method chaining
        """
        self.fact_find = FactFind()
        self.fact_find.load_from_dict(data)
        self.workflow_data['fact_find_loaded'] = datetime.now().isoformat()
        return self

    def load_automation_form(self, data: Dict[str, Any]) -> 'InsuranceWorkflow':
        """
        Load automation/recommendation form data

        Args:
            data: Automation form data dictionary

        Returns:
            Self for method chaining
        """
        self.automation_form = AutomationForm()
        self.automation_form.load_from_dict(data)
        self.workflow_data['automation_form_loaded'] = datetime.now().isoformat()
        return self

    def validate_workflow(self) -> Tuple[bool, list, list]:
        """
        Validate the complete workflow data

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Check if fact find is loaded
        if not self.fact_find:
            errors.append("Fact find form not loaded")
        else:
            # Validate fact find has required fields
            if not self.fact_find.client_info.get('email'):
                errors.append("Client email is missing from fact find")
            if not self.fact_find.case_info.get('case_id'):
                warnings.append("Case ID is missing from fact find")

        # Check if automation form is loaded
        if not self.automation_form:
            warnings.append("Automation form not loaded - recommendation data unavailable")
        else:
            # Validate automation form has required fields
            if not self.automation_form.client_details.get('email'):
                warnings.append("Client email is missing from automation form")

        # Cross-validate if both forms are loaded
        if self.fact_find and self.automation_form:
            # Check email consistency
            fact_find_email = self.fact_find.client_info.get('email')
            auto_form_email = self.automation_form.client_details.get('email')
            if fact_find_email and auto_form_email and fact_find_email != auto_form_email:
                warnings.append(f"Email mismatch: Fact find has {fact_find_email}, automation has {auto_form_email}")

            # Check couple status consistency
            fact_find_couple = self.fact_find.is_couple()
            auto_form_couple = self.automation_form.is_couple()
            if fact_find_couple != auto_form_couple:
                warnings.append(f"Couple status mismatch between forms")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    def get_client_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive client summary combining both forms

        Returns:
            Dictionary containing client summary
        """
        summary = {
            'client_info': {},
            'financial_position': {},
            'insurance_needs': {},
            'recommendations': {}
        }

        if self.fact_find:
            # Client information
            summary['client_info'] = {
                'name': self.fact_find.get_client_full_name(),
                'email': self.fact_find.client_info.get('email'),
                'date_of_birth': self.fact_find.client_info.get('date_of_birth'),
                'occupation': self.fact_find.employment_main.get('occupation') or self.fact_find.client_info.get('occupation'),
                'is_couple': self.fact_find.is_couple()
            }

            if self.fact_find.is_couple():
                summary['client_info']['partner_name'] = self.fact_find.get_partner_full_name()

            # Financial position
            summary['financial_position'] = {
                'annual_income': self.fact_find.employment_main.get('annual_income'),
                'home_value': self.fact_find.household_info.get('current_house_value'),
                'mortgage': self.fact_find.household_info.get('current_mortgage'),
                'kiwisaver_total': self._calculate_total_kiwisaver(),
                'investment_properties': len([k for k in self.fact_find.investment_properties.keys() if 'property_' in k and '_value' in k])
            }

            # Insurance needs from fact find
            summary['insurance_needs'] = {
                'life_needs': self.fact_find.needs_life_main.get('total_cover'),
                'trauma_needs': self.fact_find.needs_trauma_main.get('total'),
                'income_protection_needs': self.fact_find.needs_income_main.get('max_insurable_income')
            }

        if self.automation_form:
            # Recommendations
            summary['recommendations'] = {
                'selected_provider': self.automation_form.get_recommended_provider(),
                'scope_of_advice': self.automation_form.get_selected_scope(),
                'limitations': self.automation_form.get_limitation_reasons(),
                'quotes': self._get_all_quotes()
            }

            # Update existing insurance info
            summary['existing_insurance'] = {
                'main': {
                    'life': self.automation_form.main_existing_cover.get('life_amount'),
                    'trauma': self.automation_form.main_existing_cover.get('trauma_amount'),
                    'income_protection': self.automation_form.main_existing_cover.get('income_protection_amount'),
                    'total_premiums': self.automation_form.main_existing_cover.get('existing_premiums')
                }
            }

            if self.automation_form.is_couple():
                summary['existing_insurance']['partner'] = {
                    'life': self.automation_form.partner_existing_cover.get('life_amount'),
                    'trauma': self.automation_form.partner_existing_cover.get('trauma_amount'),
                    'income_protection': self.automation_form.partner_existing_cover.get('income_protection_amount'),
                    'total_premiums': self.automation_form.partner_existing_cover.get('existing_premiums')
                }

        return summary

    def _calculate_total_kiwisaver(self) -> Optional[float]:
        """Calculate total KiwiSaver balance"""
        if not self.fact_find:
            return None

        total = 0
        if self.fact_find.kiwisaver.get('main_balance'):
            total += self.fact_find.kiwisaver['main_balance']
        if self.fact_find.kiwisaver.get('partner_balance'):
            total += self.fact_find.kiwisaver['partner_balance']
        if self.fact_find.kiwisaver.get('balance_3'):
            total += self.fact_find.kiwisaver['balance_3']

        return total if total > 0 else None

    def _get_all_quotes(self) -> Dict[str, float]:
        """Get all provider quotes"""
        if not self.automation_form:
            return {}

        quotes = {}
        quote_fields = {
            'Partners Life': 'quote_partners_life',
            'Fidelity Life': 'quote_fidelity_life',
            'AIA': 'quote_aia',
            'Asteron': 'quote_asteron',
            'Chubb': 'quote_chubb',
            'nib': 'quote_nib'
        }

        for provider, field in quote_fields.items():
            value = self.automation_form.recommendation.get(field)
            if value:
                quotes[provider] = value

        return quotes

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive report combining both forms

        Args:
            output_path: Optional path to save the report

        Returns:
            Report content as string
        """
        summary = self.get_client_summary()

        report_lines = [
            "=" * 70,
            "INSURANCE ADVISORY REPORT",
            "=" * 70,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # Client Information Section
        report_lines.extend([
            "CLIENT INFORMATION",
            "-" * 50,
            f"Name: {summary['client_info'].get('name', 'N/A')}",
            f"Email: {summary['client_info'].get('email', 'N/A')}",
            f"Date of Birth: {summary['client_info'].get('date_of_birth', 'N/A')}",
            f"Occupation: {summary['client_info'].get('occupation', 'N/A')}",
            f"Application Type: {'Couple' if summary['client_info'].get('is_couple') else 'Single'}",
        ])

        if summary['client_info'].get('partner_name'):
            report_lines.append(f"Partner: {summary['client_info']['partner_name']}")

        report_lines.append("")

        # Financial Position Section
        if summary['financial_position']:
            report_lines.extend([
                "FINANCIAL POSITION",
                "-" * 50
            ])

            fin_pos = summary['financial_position']
            if fin_pos.get('annual_income'):
                report_lines.append(f"Annual Income: ${fin_pos['annual_income']:,.0f}")
            if fin_pos.get('home_value'):
                report_lines.append(f"Home Value: ${fin_pos['home_value']:,.0f}")
            if fin_pos.get('mortgage'):
                report_lines.append(f"Mortgage: ${fin_pos['mortgage']:,.0f}")
            if fin_pos.get('kiwisaver_total'):
                report_lines.append(f"Total KiwiSaver: ${fin_pos['kiwisaver_total']:,.0f}")
            if fin_pos.get('investment_properties'):
                report_lines.append(f"Investment Properties: {fin_pos['investment_properties']}")

            report_lines.append("")

        # Existing Insurance Section
        if summary.get('existing_insurance'):
            report_lines.extend([
                "EXISTING INSURANCE",
                "-" * 50
            ])

            if 'main' in summary['existing_insurance']:
                main_ins = summary['existing_insurance']['main']
                report_lines.append("Main Contact:")
                if main_ins.get('life'):
                    report_lines.append(f"  Life Cover: ${main_ins['life']:,.0f}")
                if main_ins.get('trauma'):
                    report_lines.append(f"  Trauma Cover: ${main_ins['trauma']:,.0f}")
                if main_ins.get('income_protection'):
                    report_lines.append(f"  Income Protection: ${main_ins['income_protection']:,.0f}/month")
                if main_ins.get('total_premiums'):
                    report_lines.append(f"  Current Premiums: ${main_ins['total_premiums']:,.0f}/month")

            if 'partner' in summary['existing_insurance']:
                partner_ins = summary['existing_insurance']['partner']
                report_lines.append("\nPartner:")
                if partner_ins.get('life'):
                    report_lines.append(f"  Life Cover: ${partner_ins['life']:,.0f}")
                if partner_ins.get('trauma'):
                    report_lines.append(f"  Trauma Cover: ${partner_ins['trauma']:,.0f}")
                if partner_ins.get('income_protection'):
                    report_lines.append(f"  Income Protection: ${partner_ins['income_protection']:,.0f}/month")
                if partner_ins.get('total_premiums'):
                    report_lines.append(f"  Current Premiums: ${partner_ins['total_premiums']:,.0f}/month")

            report_lines.append("")

        # Recommendations Section
        if summary['recommendations']:
            report_lines.extend([
                "RECOMMENDATIONS",
                "-" * 50
            ])

            rec = summary['recommendations']
            if rec.get('selected_provider'):
                report_lines.append(f"Recommended Provider: {rec['selected_provider']}")
            if rec.get('scope_of_advice'):
                report_lines.append(f"Scope: {', '.join(rec['scope_of_advice'])}")
            if rec.get('limitations'):
                report_lines.append(f"Limitations: {', '.join(rec['limitations'])}")

            if rec.get('quotes'):
                report_lines.append("\nProvider Quotes:")
                for provider, quote in sorted(rec['quotes'].items(), key=lambda x: x[1]):
                    selected = " ← SELECTED" if provider == rec.get('selected_provider') else ""
                    report_lines.append(f"  {provider:20} ${quote:,.0f}/month{selected}")

            report_lines.append("")

        # Footer
        report_lines.extend([
            "=" * 70,
            "END OF REPORT",
            "=" * 70
        ])

        report_content = "\n".join(report_lines)

        # Save to file if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report_content)

        return report_content

    def to_dict(self) -> Dict[str, Any]:
        """Export complete workflow data as dictionary"""
        return {
            'workflow_data': self.workflow_data,
            'fact_find': self.fact_find.to_dict() if self.fact_find else None,
            'automation_form': self.automation_form.to_dict() if self.automation_form else None,
            'client_summary': self.get_client_summary()
        }

    def to_json(self, indent: int = 2) -> str:
        """Export complete workflow data as JSON"""
        return json.dumps(self.to_dict(), indent=indent, default=str)