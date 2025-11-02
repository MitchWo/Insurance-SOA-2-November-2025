#!/usr/bin/env python3
"""
Scope of Advice JSON Generator

This module provides functionality to generate structured JSON for the scope of advice
section of an insurance Statement of Advice (SOA) report.

It processes checkbox fields from automation forms to determine which insurance products
are in or out of scope, maps limitation reasons to out-of-scope products, and generates
a comprehensive JSON structure for LLM-based prose generation.

Created: 2025-01-27
Author: Insurance SOA System
License: Lighthouse Financial
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class ScopeOfAdviceGenerator:
    """Generator for scope of advice JSON structures"""

    # Insurance product mapping
    INSURANCE_PRODUCTS = {
        '5.1': 'Life Insurance',
        '5.2': 'Income Protection',
        '5.3': 'Trauma Cover',
        '5.4': 'Health Insurance',
        '5.5': 'Total Permanent Disability (TPD)',
        '5.6': 'ACC Top-Up'
    }

    # Limitation reasons mapping
    LIMITATION_REASONS = {
        '6.1': 'employer_medical',
        '6.2': 'no_debt_strong_assets',
        '6.3': 'budget_limitations',
        '6.4': 'self_insure',
        '6.5': 'no_dependants',
        '6.6': 'uninsurable_occupation',
        '6.7': 'other'
    }

    # Human-readable limitation descriptions
    LIMITATION_DESCRIPTIONS = {
        'employer_medical': 'Medical cover provided through employer',
        'no_debt_strong_assets': 'No debt and strong asset base eliminates need for life cover',
        'budget_limitations': 'Budget constraints limit insurance options',
        'self_insure': 'Client has sufficient assets to self-insure risks',
        'no_dependants': 'No financial dependants requiring protection',
        'uninsurable_occupation': 'Occupation is not insurable or has significant loadings',
        'other': 'Other reasons (see notes)'
    }

    # Map limitations to commonly affected products
    LIMITATION_TO_PRODUCTS_MAP = {
        'employer_medical': ['Health Insurance'],
        'no_debt_strong_assets': ['Life Insurance'],
        'budget_limitations': ['all'],  # Can affect any product
        'self_insure': ['Income Protection', 'Trauma Cover', 'Health Insurance'],
        'no_dependants': ['Life Insurance'],
        'uninsurable_occupation': ['Income Protection', 'Total Permanent Disability (TPD)'],
        'other': ['all']  # Can affect any product
    }

    @classmethod
    def generate_scope_json(cls,
                           raw_form_data: Dict[str, Any],
                           client_name: Optional[str] = None,
                           is_couple: bool = False) -> Dict[str, Any]:
        """
        Generate comprehensive JSON structure for scope of advice

        Args:
            raw_form_data: Raw form data from Gravity Forms containing fields:
                - f5 or 5: Main scope checkbox field
                - f5.1-f5.6 or 5.1-5.6: Individual insurance type checkboxes
                - f6 or 6: Main limitations checkbox field
                - f6.1-f6.7 or 6.1-6.7: Individual limitation reason checkboxes
                - f7 or 7: Additional limitation notes text field
                - date_created: Form submission timestamp (WordPress format)
            client_name: Optional client name for personalization
            is_couple: Whether this is for a couple (affects pronouns/context)

        Returns:
            Structured JSON containing raw data, processed scope, and prose generation context
        """
        # Extract and process form fields
        scope_fields = cls._extract_scope_fields(raw_form_data)
        limitation_fields = cls._extract_limitation_fields(raw_form_data)
        limitation_notes = cls._extract_limitation_notes(raw_form_data)
        form_submission_date = cls._extract_and_format_date(raw_form_data)

        # Determine in-scope and out-of-scope products
        in_scope, out_of_scope = cls._process_scope(scope_fields)

        # Process limitation reasons
        active_limitations = cls._process_limitations(limitation_fields)

        # Map limitations to out-of-scope products
        limitation_product_mapping = cls._map_limitations_to_products(
            active_limitations, out_of_scope
        )

        # Build the lean JSON structure - only essential fields for Zapier
        sections = {
            "limitations": cls._generate_limitations_content(
                active_limitations, limitation_notes
            )
        }

        # Add form submission date if available
        if form_submission_date:
            sections["form_submission_date"] = form_submission_date

        return {
            "section_type": "scope_of_advice",
            "products_in_scope": in_scope,
            "products_out_of_scope": out_of_scope,
            "sections": sections
        }

    @classmethod
    def _get_field_value(cls, data: Dict[str, Any], field_id: str) -> Optional[Any]:
        """Extract field value trying both with and without 'f' prefix"""
        # Try with 'f' prefix first
        f_key = f"f{field_id}"
        if f_key in data:
            return data[f_key]

        # Try without prefix
        if field_id in data:
            return data[field_id]

        return None

    @classmethod
    def _extract_scope_fields(cls, data: Dict[str, Any]) -> Dict[str, bool]:
        """Extract scope checkbox fields and convert to boolean values"""
        scope_fields = {}

        for field_id, product_name in cls.INSURANCE_PRODUCTS.items():
            value = cls._get_field_value(data, field_id)
            scope_fields[product_name] = cls._is_checked(value)

        return scope_fields

    @classmethod
    def _extract_limitation_fields(cls, data: Dict[str, Any]) -> Dict[str, bool]:
        """Extract limitation checkbox fields and convert to boolean values"""
        limitation_fields = {}

        for field_id, reason_code in cls.LIMITATION_REASONS.items():
            value = cls._get_field_value(data, field_id)
            limitation_fields[reason_code] = cls._is_checked(value)

        return limitation_fields

    @classmethod
    def _extract_limitation_notes(cls, data: Dict[str, Any]) -> str:
        """Extract limitation notes text field"""
        notes = cls._get_field_value(data, '7')
        return str(notes) if notes else ""

    @classmethod
    def _extract_and_format_date(cls, data: Dict[str, Any]) -> Optional[str]:
        """Extract date_created from form data and format as 'Day, DD Month YYYY'"""
        date_str = data.get('date_created')
        if not date_str:
            return None

        try:
            # Parse WordPress format: "2025-10-30 01:13:38"
            dt = datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
            # Format as "Wednesday, 30 October 2025"
            return dt.strftime("%A, %d %B %Y")
        except (ValueError, TypeError):
            return None

    @classmethod
    def _is_checked(cls, value: Any) -> bool:
        """Convert various checkbox representations to boolean"""
        if value is None or value == "":
            return False

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value_lower = value.lower().strip()
            # Check for explicit checkbox markers
            if value_lower in ['yes', 'true', '1', 'checked', 'on', 'x']:
                return True
            # If it's a non-empty string and not empty, treat as selected
            # (covers cases where form stores product names or descriptions in checkbox fields)
            return len(value_lower) > 0

        return bool(value)

    @classmethod
    def _process_scope(cls, scope_fields: Dict[str, bool]) -> Tuple[List[str], List[str]]:
        """Determine which products are in scope and out of scope"""
        in_scope = []
        out_of_scope = []

        for product, is_selected in scope_fields.items():
            if is_selected:
                in_scope.append(product)
            else:
                out_of_scope.append(product)

        return in_scope, out_of_scope

    @classmethod
    def _process_limitations(cls, limitation_fields: Dict[str, bool]) -> List[Dict[str, str]]:
        """Process active limitations into structured format"""
        active_limitations = []

        for reason_code, is_active in limitation_fields.items():
            if is_active:
                active_limitations.append({
                    'code': reason_code,
                    'description': cls.LIMITATION_DESCRIPTIONS.get(
                        reason_code, 'Unknown limitation'
                    )
                })

        return active_limitations

    @classmethod
    def _map_limitations_to_products(cls,
                                    active_limitations: List[Dict[str, str]],
                                    out_of_scope: List[str]) -> Dict[str, List[str]]:
        """Map active limitations to out-of-scope products"""
        mapping = {}

        for limitation in active_limitations:
            code = limitation['code']
            affected_products = cls.LIMITATION_TO_PRODUCTS_MAP.get(code, [])

            # Filter to only include products that are actually out of scope
            if 'all' in affected_products:
                # This limitation can affect all products
                relevant_products = out_of_scope
            else:
                # Only include products that are both affected and out of scope
                relevant_products = [p for p in affected_products if p in out_of_scope]

            if relevant_products:
                mapping[code] = relevant_products

        return mapping

    @classmethod
    def _generate_opening_statement(cls, in_scope: List[str], out_of_scope: List[str]) -> str:
        """Generate opening statement based on scope"""
        if not in_scope:
            return "After careful consideration of your circumstances, we are not recommending any insurance products at this time."
        elif not out_of_scope:
            return "Our advice encompasses a comprehensive insurance portfolio covering all major risk areas."
        else:
            return f"Based on your specific circumstances and requirements, our advice will focus on {len(in_scope)} insurance product(s)."

    @classmethod
    def _generate_limitation_explanations(cls,
                                         active_limitations: List[Dict[str, str]],
                                         limitation_mapping: Dict[str, List[str]],
                                         limitation_notes: str) -> List[str]:
        """Generate explanations for each limitation"""
        explanations = []

        for limitation in active_limitations:
            code = limitation['code']
            description = limitation['description']
            affected_products = limitation_mapping.get(code, [])

            if affected_products:
                products_str = ", ".join(affected_products)
                explanation = f"{description} - affecting: {products_str}"

                # Add notes for 'other' reason
                if code == 'other' and limitation_notes:
                    explanation += f" (Details: {limitation_notes})"

                explanations.append(explanation)

        return explanations

    @classmethod
    def _generate_closing_statement(cls, in_scope: List[str], is_couple: bool) -> str:
        """Generate closing statement"""
        if not in_scope:
            return "We remain available to review your insurance needs should your circumstances change."

        pronoun = "your" if not is_couple else "your family's"
        return f"Our recommendations will focus on optimizing {pronoun} coverage for the selected products while ensuring the solution remains affordable and appropriate for your situation."

    @classmethod
    def _generate_summary(cls, in_scope: List[str], out_of_scope: List[str],
                         client_name: Optional[str], is_couple: bool) -> str:
        """Generate summary content for scope section"""
        client_ref = client_name or ("your family" if is_couple else "you")

        if not in_scope:
            return f"After reviewing the financial situation and insurance needs for {client_ref}, no insurance products are being recommended at this time. This decision is based on current circumstances including existing coverage, financial position, and identified limitations."
        elif not out_of_scope:
            return f"This Statement of Advice provides comprehensive insurance recommendations for {client_ref} covering all major risk areas including life, income protection, trauma, health, TPD, and ACC top-up insurance. Our analysis indicates that full coverage across all product categories is appropriate."
        else:
            scope_str = ", ".join(in_scope[:3]) + ("..." if len(in_scope) > 3 else "")
            return f"This advice focuses on {len(in_scope)} insurance product(s) for {client_ref}: {scope_str}. The scope has been tailored based on specific needs, existing coverage, and identified circumstances that limit the requirement for certain insurance types."

    @classmethod
    def _generate_in_scope_content(cls, in_scope: List[str]) -> str:
        """Generate content for in-scope products section"""
        if not in_scope:
            return "No insurance products are currently being advised on based on the assessment."

        products_list = ", ".join(in_scope)
        return f"The following insurance products are included in this advice: {products_list}. Detailed recommendations and premium quotations for these products are provided in subsequent sections."

    @classmethod
    def _generate_out_of_scope_content(cls, out_of_scope: List[str],
                                      active_limitations: List[Dict[str, str]],
                                      limitation_mapping: Dict[str, List[str]]) -> str:
        """Generate content for out-of-scope products section"""
        if not out_of_scope:
            return "All standard insurance product categories have been included in this advice with no exclusions."

        products_list = ", ".join(out_of_scope)
        reason = "due to identified limitations" if active_limitations else "based on needs analysis"
        return f"The following products are not included in this advice {reason}: {products_list}. These exclusions are based on factors detailed in the limitations section."

    @classmethod
    def _generate_limitations_content(cls, active_limitations: List[Dict[str, str]],
                                     limitation_notes: str) -> str:
        """Generate content for limitations section"""
        if not active_limitations:
            return "No specific limitations have been identified that restrict the scope of insurance advice."

        limitations_text = "; ".join([lim['description'] for lim in active_limitations[:3]])
        if len(active_limitations) > 3:
            limitations_text += f" and {len(active_limitations) - 3} other factor(s)"

        if limitation_notes:
            limitations_text += f". Additional notes: {limitation_notes[:100]}"

        return f"Scope limitations: {limitations_text}"

    @classmethod
    def _generate_assumptions_content(cls, in_scope: List[str], out_of_scope: List[str],
                                     is_couple: bool) -> str:
        """Generate content for assumptions section"""
        assumptions = []

        if in_scope:
            assumptions.append("client requires protection for insurable risks identified")
        if out_of_scope:
            assumptions.append("excluded products are not currently required or suitable")
        if is_couple:
            assumptions.append("both partners' insurance needs have been considered jointly")

        if not assumptions:
            assumptions = ["standard underwriting terms will apply", "disclosed information is complete and accurate"]

        return f"This advice assumes: {'; '.join(assumptions)}; premiums quoted are estimates subject to underwriting; client's circumstances may change requiring review."

    @classmethod
    def _generate_client_priorities_content(cls, in_scope: List[str],
                                          active_limitations: List[Dict[str, str]],
                                          is_couple: bool) -> str:
        """Generate content for client priorities section"""
        priorities = []

        if "Life Insurance" in in_scope:
            priorities.append("protect family/beneficiaries from financial hardship")
        if "Income Protection" in in_scope:
            priorities.append("maintain income during disability")
        if "Health Insurance" in in_scope:
            priorities.append("access to private healthcare")

        # Add budget priority if budget limitation exists
        if any(lim['code'] == 'budget_limitations' for lim in active_limitations):
            priorities.append("keep premiums within budget constraints")

        if not priorities:
            priorities = ["obtain appropriate insurance coverage", "balance protection with affordability"]

        priority_text = "; ".join(priorities[:4])
        return f"Client priorities identified: {priority_text}"

    @classmethod
    def _generate_replacements_content(cls, in_scope: List[str]) -> str:
        """Generate content for replacements section"""
        if not in_scope:
            return "No existing insurance products are being recommended for replacement."

        return "Any replacement of existing policies will be clearly identified with detailed comparisons. Replacement is only recommended where new cover provides superior benefits or better value. Existing cover should be maintained until new cover is in place."

    @classmethod
    def _generate_not_covered_content(cls, out_of_scope: List[str]) -> str:
        """Generate content for what is not covered section"""
        if not out_of_scope:
            return "This advice covers all major insurance categories. Specific policy exclusions and limitations will apply as per policy terms."

        exclusions = []
        if "Health Insurance" in out_of_scope:
            exclusions.append("private medical treatment costs")
        if "Income Protection" in out_of_scope:
            exclusions.append("loss of income due to disability")
        if "Life Insurance" in out_of_scope:
            exclusions.append("death benefit for beneficiaries")

        if exclusions:
            return f"Not covered under this advice: {'; '.join(exclusions[:3])}. Clients should consider self-insurance or alternative arrangements for these risks."

        return "Products outside the agreed scope are not covered. Policy-specific exclusions will apply to recommended products."

    @classmethod
    def _generate_next_steps_content(cls, in_scope: List[str], out_of_scope: List[str]) -> str:
        """Generate content for next steps section"""
        if not in_scope:
            return "Review insurance needs annually or when circumstances change. Contact adviser if situation changes requiring insurance coverage."

        steps = [
            "Review recommended products and premiums",
            "Complete application forms for selected insurance",
            "Undergo any required underwriting",
            "Implement accepted coverage"
        ]

        return f"Next steps: {'; '.join(steps[:3])}. Adviser will guide through application process."

    @classmethod
    def _generate_disclosures_content(cls) -> str:
        """Generate content for disclosures section"""
        return "This advice is based on information provided and current legislation. Insurance products have exclusions, limitations, and terms that affect coverage. Premiums may vary from quotes based on underwriting. Tax implications should be considered. Seek independent advice if uncertain."

    @classmethod
    def _generate_example_prose(cls,
                               in_scope: List[str],
                               out_of_scope: List[str],
                               active_limitations: List[Dict[str, str]],
                               limitation_notes: str,
                               client_name: Optional[str],
                               is_couple: bool) -> str:
        """Generate example prose output"""
        client_ref = client_name or "the client"
        pronoun = "their" if is_couple else "your"

        prose_parts = []

        # Opening
        prose_parts.append("## Scope of Advice\n")

        # In-scope products
        if in_scope:
            prose_parts.append(f"Following our comprehensive needs analysis, we will be providing recommendations for the following insurance products:\n")
            for product in in_scope:
                prose_parts.append(f"• {product}")
            prose_parts.append("")

        # Out-of-scope products and limitations
        if out_of_scope:
            prose_parts.append("\nThe following products are not included in our current recommendations:\n")
            for product in out_of_scope:
                prose_parts.append(f"• {product}")

            if active_limitations:
                prose_parts.append("\nThis scope has been determined based on the following factors:\n")
                for limitation in active_limitations:
                    desc = limitation['description']
                    if limitation['code'] == 'other' and limitation_notes:
                        desc += f" - {limitation_notes}"
                    prose_parts.append(f"• {desc}")

        # Closing
        prose_parts.append(f"\nOur recommendations will be tailored to {pronoun} specific needs and circumstances, focusing on providing appropriate coverage within the agreed scope.")

        return "\n".join(prose_parts)


def generate_scope_of_advice_json(raw_form_data: Dict[str, Any],
                                 client_name: Optional[str] = None,
                                 is_couple: bool = False) -> Dict[str, Any]:
    """
    Main function to generate scope of advice JSON structure

    Args:
        raw_form_data: Raw form data from Gravity Forms
        client_name: Optional client name for personalization
        is_couple: Whether this is for a couple

    Returns:
        Structured JSON for scope of advice section
    """
    return ScopeOfAdviceGenerator.generate_scope_json(
        raw_form_data, client_name, is_couple
    )


# Example usage and testing
if __name__ == "__main__":
    # Example form data
    example_data = {
        "f5": "checked",
        "f5.1": "Yes",  # Life Insurance
        "f5.2": "Yes",  # Income Protection
        "f5.3": "No",   # Trauma Cover
        "f5.4": "No",   # Health Insurance
        "f5.5": "Yes",  # TPD
        "f5.6": "No",   # ACC
        "f6": "checked",
        "f6.1": "Yes",  # Employer medical
        "f6.3": "Yes",  # Budget limitations
        "f7": "Client has comprehensive medical coverage through employer's group scheme"
    }

    # Generate JSON structure
    result = generate_scope_of_advice_json(
        example_data,
        client_name="John Smith",
        is_couple=False
    )

    # Pretty print the result
    print(json.dumps(result, indent=2))