"""
Zapier Webhook Trigger
Automatically sends combined insurance data to Zapier when forms are matched
"""

import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import time
from datetime import datetime
from processors.zapier_payload_builder import ZapierPayloadBuilder


class ZapierTrigger:
    """Handles sending data to Zapier webhooks"""

    def __init__(self, config_path: str = None):
        """Initialize with configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "zapier_config.json"

        self.config = self._load_config(config_path)
        self.enabled = self.config.get('enabled', False)
        self.webhook_url = self.config.get('zapier_webhook_url', '')
        self.payload_builder = ZapierPayloadBuilder()

    def _load_config(self, config_path: Path) -> Dict:
        """Load Zapier configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load Zapier config: {e}")
            return {
                'enabled': False,
                'zapier_webhook_url': '',
                'retry_attempts': 3,
                'retry_delay_seconds': 5,
                'timeout_seconds': 30,
                'headers': {'Content-Type': 'application/json'}
            }

    def _flatten_data(self, data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        Flatten nested dictionaries for Zapier compatibility.
        Converts nested structures to flat key-value pairs like:
        personal_information_main_contact_name instead of data['personal_information']['main_contact']['name']

        Args:
            data: The data to flatten
            parent_key: The parent key for recursion
            sep: Separator between keys

        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            # Skip scope_of_advice sections field - only keep limitations and products
            if parent_key == 'scope_of_advice' and k == 'sections':
                # Extract only limitations, in_scope, and out_of_scope from sections
                if isinstance(v, dict):
                    if 'limitations' in v:
                        items.append((f"{parent_key}{sep}sections{sep}limitations", v['limitations']))
                    if 'in_scope' in v:
                        items.append((f"{parent_key}{sep}products_in_scope", v['in_scope']))
                    if 'out_of_scope' in v:
                        items.append((f"{parent_key}{sep}products_out_of_scope", v['out_of_scope']))
                continue

            # For personal_information, create table format
            if k in ['personal_information']:
                if isinstance(v, dict):
                    # Create a flat table representation
                    table_data = []
                    for field_name, field_value in v.items():
                        if field_name != 'section_type':
                            table_data.append({
                                'field': field_name,
                                'value': str(field_value)
                            })
                    items.append((new_key, json.dumps(table_data)))
                    # Also add section_type
                    if 'section_type' in v:
                        items.append((f"{new_key}{sep}section_type", v['section_type']))
                continue

            if isinstance(v, dict):
                # Recursively flatten nested dicts
                items.extend(self._flatten_data(v, new_key, sep=sep).items())
            elif isinstance(v, (list, tuple)):
                # For lists, convert to JSON string so Zapier can handle it
                items.append((new_key, json.dumps(v)))
            else:
                # Keep scalar values as-is
                items.append((new_key, v))

        return dict(items)

    def trigger(self, combined_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send combined data to Zapier webhook

        Args:
            combined_data: The combined report data to send

        Returns:
            Response data including status and any errors
        """
        response = {
            'triggered': False,
            'timestamp': datetime.now().isoformat(),
            'status': 'disabled',
            'message': '',
            'zapier_response': None
        }

        if not self.enabled:
            response['message'] = 'Zapier trigger is disabled'
            print("📌 Zapier trigger disabled - skipping webhook")
            return response

        if not self.webhook_url or self.webhook_url == 'YOUR_ZAPIER_WEBHOOK_URL_HERE':
            response['status'] = 'not_configured'
            response['message'] = 'Zapier webhook URL not configured'
            print("⚠️ Zapier webhook URL not configured")
            return response

        print("=" * 70)
        print("🚀 TRIGGERING ZAPIER WEBHOOK")
        print("=" * 70)
        print(f"URL: {self.webhook_url}")
        print(f"Data fields: {len(combined_data)} fields")

        # Build standardized payload
        payload = self.payload_builder.build_payload(combined_data)

        # Validate payload
        is_valid, errors = self.payload_builder.validate_payload(payload)
        if not is_valid:
            print("⚠️ WARNING: Payload validation errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ Payload validation passed")

        # Print summary
        print("\nPayload Summary:")
        print(self.payload_builder.get_payload_summary(payload))

        # Try to send with retries
        attempts = self.config.get('retry_attempts', 3)
        retry_delay = self.config.get('retry_delay_seconds', 5)
        timeout = self.config.get('timeout_seconds', 30)
        headers = self.config.get('headers', {'Content-Type': 'application/json'})

        for attempt in range(1, attempts + 1):
            try:
                print(f"Attempt {attempt}/{attempts}...")

                # Send the webhook
                r = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )

                # Check response
                if r.status_code in [200, 201, 202]:
                    response['triggered'] = True
                    response['status'] = 'success'
                    response['message'] = f'Successfully triggered Zapier webhook (HTTP {r.status_code})'
                    response['zapier_response'] = {
                        'status_code': r.status_code,
                        'response_text': r.text[:500] if r.text else None
                    }
                    print(f"✅ Success! Zapier responded with status {r.status_code}")
                    break
                else:
                    error_msg = f'Zapier returned status {r.status_code}: {r.text[:200]}'
                    print(f"⚠️ {error_msg}")
                    response['message'] = error_msg
                    response['status'] = 'error'

                    if attempt < attempts:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)

            except requests.exceptions.Timeout:
                error_msg = f'Request timed out after {timeout} seconds'
                print(f"⏱️ {error_msg}")
                response['message'] = error_msg
                response['status'] = 'timeout'

            except requests.exceptions.RequestException as e:
                error_msg = f'Request failed: {str(e)}'
                print(f"❌ {error_msg}")
                response['message'] = error_msg
                response['status'] = 'error'

            except Exception as e:
                error_msg = f'Unexpected error: {str(e)}'
                print(f"💥 {error_msg}")
                response['message'] = error_msg
                response['status'] = 'error'

        print("=" * 70)
        return response


def test_zapier_trigger():
    """Test the Zapier trigger with sample data"""

    # Create trigger instance
    trigger = ZapierTrigger()

    # Sample data
    test_data = {
        'client_name': 'Test Client',
        'is_couple': False,
        'life_insurance': {
            'main_needs_insurance': True,
            'main_total_needs': 225000,
            'main_net_coverage': 125000
        },
        'trauma_insurance': {
            'main_needs_trauma': True,
            'main_total_trauma': 81000
        },
        'income_protection': {
            'main_needs_income_protection': True,
            'main_monthly_benefit': 5000
        },
        'health_insurance': {
            'main_needs_health_insurance': True,
            'main_plan_type': 'premium'
        },
        'accidental_injury': {
            'main_needs_accident_cover': True,
            'acc_topup_recommended': True
        }
    }

    # Trigger webhook
    result = trigger.trigger(test_data)

    print("\nTrigger Result:")
    print(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    test_zapier_trigger()