"""
Insurance Quotes Extractor
Extracts insurance quote upload URLs from automation form fields
"""

import json
from typing import Dict, Any


def extract_quote_url(field_value: Any) -> str:
    """
    Extract URL from quote field JSON format

    Fields contain JSON arrays like: [{"name":"filename.pdf","url":"https://..."}]
    """
    if not field_value:
        return ""

    try:
        # If it's already a string that looks like JSON, parse it
        if isinstance(field_value, str) and field_value.startswith('['):
            quote_data = json.loads(field_value)
            if quote_data and len(quote_data) > 0:
                # Get the first item's URL
                return quote_data[0].get('url', '')
        # If it's just a plain URL string, return it
        elif isinstance(field_value, str) and field_value.startswith('http'):
            return field_value
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return ""


def extract_insurance_quotes(combined_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract insurance quote URLs from automation form fields

    Field IDs:
    - 42: Partners Life quote
    - 43: Fidelity Life quote
    - 44: AIA quote
    - 45: Asteron quote
    - 46: Chubb quote
    - 47: nib quote

    Returns:
        Dictionary with individual quote URLs for each provider
    """

    # Extract quote URLs from the form fields
    quote_partners_life = extract_quote_url(combined_data.get('42', ''))
    quote_fidelity_life = extract_quote_url(combined_data.get('43', ''))
    quote_aia = extract_quote_url(combined_data.get('44', ''))
    quote_asteron = extract_quote_url(combined_data.get('45', ''))
    quote_chubb = extract_quote_url(combined_data.get('46', ''))
    quote_nib = extract_quote_url(combined_data.get('47', ''))

    # Count how many quotes were uploaded
    quotes_count = sum([
        1 for url in [
            quote_partners_life,
            quote_fidelity_life,
            quote_aia,
            quote_asteron,
            quote_chubb,
            quote_nib
        ] if url
    ])

    return {
        "section_id": "insurance_quotes",
        "section_type": "quote_uploads",

        # Individual quote URLs (for Zapier)
        "quote_partners_life": quote_partners_life,
        "quote_fidelity_life": quote_fidelity_life,
        "quote_aia": quote_aia,
        "quote_asteron": quote_asteron,
        "quote_chubb": quote_chubb,
        "quote_nib": quote_nib,

        # Metadata
        "quotes_count": quotes_count,
        "has_quotes": quotes_count > 0,

        "status": "success"
    }