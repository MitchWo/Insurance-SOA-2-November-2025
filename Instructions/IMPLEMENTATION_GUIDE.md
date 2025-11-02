# Implementation Guide - Insurance SOA System

## Overview
This guide provides developers with detailed information on how to extend, modify, or integrate with the Insurance SOA System.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Gravity Forms                             │
│         (WordPress Form Submission)                          │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
             ▼                                ▼
      ┌──────────────┐              ┌──────────────┐
      │  Fact Find   │              │ Automation   │
      │    Form      │              │    Form      │
      └──────┬───────┘              └──────┬───────┘
             │                             │
             └────────────┬────────────────┘
                          ▼
            ┌──────────────────────────┐
            │   Webhook Server (5001)  │
            │  - Form Reception        │
            │  - Form Matching         │
            │  - Data Extraction       │
            └──────────────┬───────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
   ┌──────────────────┐     ┌─────────────────────┐
   │  Extractors      │     │  Generators         │
   │ - Personal Info  │     │ - Life Insurance    │
   │ - Assets/Liabs   │     │ - Trauma Cover      │
   │ - Scope of Advice│     │ - Income Protection │
   └────────┬─────────┘     └────────┬────────────┘
            │                        │
            └────────────┬───────────┘
                         ▼
            ┌──────────────────────────┐
            │  Zapier Webhook Trigger  │
            │  (HTTP POST)             │
            └──────────────┬───────────┘
                          ▼
                   ┌──────────────┐
                   │   Zapier     │
                   │ Automation   │
                   └──────────────┘
```

---

## Key Components

### 1. Webhook Server (`src/webhook_server.py`)

**Purpose**: Main entry point for form submissions

**Key Functions**:
- Load existing forms on startup
- Receive and store form data
- Match fact find with automation form
- Trigger report generation
- Send to Zapier

**Key Classes**:
- `FormMatcher`: Matches forms by email and confidence
- `InsuranceWorkflow`: Generates comprehensive reports
- `ZapierTrigger`: Sends data to Zapier webhook

**Startup Process**:
```python
# 1. Initialize Flask app
app = Flask(__name__)

# 2. Load existing forms
load_all_forms()

# 3. Initialize components
matcher = FormMatcher()
zapier_trigger = ZapierTrigger()

# 4. Start server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

---

### 2. Form Matcher (`src/processors/form_matcher.py`)

**Purpose**: Match fact find and automation forms by email

**Algorithm**:
1. Extract email from both form types
2. Calculate confidence score based on:
   - Email match
   - Date proximity
   - Data completeness
3. Return match if confidence > threshold (0.7)

**Usage**:
```python
from processors.form_matcher import FormMatcher

matcher = FormMatcher()

# Add forms
matcher.add_fact_find(fact_find_obj)
matcher.add_automation_form(automation_obj)

# Match by email
match_result = matcher.match_by_email("user@example.com")

if match_result and match_result.is_confident_match(0.7):
    print("Match found!")
    print(f"Confidence: {match_result.confidence}")
```

---

### 3. Data Extractors

#### Personal Information Extractor
```python
from processors.personal_information_extractor import extract_personal_information

result = extract_personal_information(combined_data)
# Returns: {section_type, is_couple, client_*, partner_*, etc.}
```

**Field Extraction Order**:
1. Try primary field ID
2. Fallback to alternate field ID
3. Return empty string if not found

**Implementation Example**:
```python
def safe_get(data, field, default=""):
    return data.get(field, default) if data else default

# Try field 144, fallback to field 3
name = safe_get(combined_data, "144", safe_get(combined_data, "3", ""))
```

---

#### Assets & Liabilities Extractor
```python
from processors.assets_liabilities_extractor import extract_assets_liabilities

result = extract_assets_liabilities(combined_data)
# Returns: property, KiwiSaver, liabilities, net worth
```

**Key Calculations**:
```python
# Property
property_equity = property_value - mortgage_balance

# Total Assets
total_assets = property_value + kiwisaver_balance + other_assets

# Total Liabilities
total_liabilities = mortgage_balance + other_debts

# Net Worth
net_worth = total_assets - total_liabilities

# Ratios
debt_to_asset_ratio = (total_liabilities / total_assets) * 100
```

---

### 4. Generators

#### Life Insurance Fields Generator
```python
from generators.life_insurance_fields import extract_life_insurance_fields

result = extract_life_insurance_fields(form_data)
```

**Calculation Logic**:
```python
# Main contact
main_total_needs = (debt + replacement_income + education +
                   final_expenses + other_considerations)
main_total_offsets = assets + kiwisaver
main_net_coverage = max(0, total_needs - total_offsets)

# Coverage levels
if net_coverage == 0:
    coverage_level = "none"
elif net_coverage < 250000:
    coverage_level = "basic"
elif net_coverage < 750000:
    coverage_level = "moderate"
else:
    coverage_level = "comprehensive"
```

---

#### Scope of Advice Generator
```python
from processors.scope_of_advice_generator import generate_scope_of_advice_json

result = generate_scope_of_advice_json(combined_data, client_name, is_couple)
```

**Key Features**:
1. **Checkbox Detection**
   - Recognizes: 'yes', 'true', '1', 'checked', 'on', 'x'
   - Handles product names: 'Life Insurance'
   - Any non-empty string = checked

2. **Date Formatting**
   - Input: "2025-10-30 01:13:38" (WordPress format)
   - Output: "Thursday, 30 October 2025"
   - Uses: `datetime.strftime("%A, %d %B %Y")`

3. **Limitation Mapping**
   - Maps limitations to affected products
   - Only includes limitations that apply to out-of-scope products

---

### 5. Zapier Trigger (`src/processors/zapier_trigger.py`)

**Purpose**: Send data to Zapier webhook

**Implementation**:
```python
from processors.zapier_trigger import ZapierTrigger

zapier = ZapierTrigger()

# Prepare data
data = {
    'personal_information': {...},
    'life_insurance': {...},
    'scope_of_advice': {...},
    # ... other sections
}

# Trigger webhook
result = zapier.trigger(data)
# Returns: {triggered: bool, status: str, message: str}
```

**Data Flattening**:
The system flattens nested JSON structures for Zapier compatibility:
```python
# Input: nested structure
{
    "personal_information": {
        "client_name": "John",
        "client_age": "45"
    }
}

# Output: flattened
{
    "personal_information_client_name": "John",
    "personal_information_client_age": "45"
}
```

**Retry Logic**:
```python
# Attempt 1: Immediate
# Attempt 2: After 2 seconds
# Attempt 3: After 4 seconds
```

---

## Adding New Features

### Example 1: Add New Insurance Type

**Step 1**: Create generator file
```python
# src/generators/travel_insurance_fields.py
def extract_travel_insurance_fields(form_data):
    return {
        "section_type": "travel_insurance",
        "annual_trips": form_data.get("field_123", ""),
        "trip_duration": form_data.get("field_124", ""),
        "coverage_needed": True
    }
```

**Step 2**: Import in auto_matcher.py
```python
from generators.travel_insurance_fields import extract_travel_insurance_fields
```

**Step 3**: Add to report generation
```python
travel_insurance = extract_travel_insurance_fields(combined_data)
combined_report['travel_insurance'] = travel_insurance
```

**Step 4**: Add webhook endpoint
```python
@app.route('/generate/travel-insurance-fields', methods=['POST'])
def generate_travel_insurance():
    data = request.get_json()
    result = extract_travel_insurance_fields(data)
    return jsonify(result), 200
```

---

### Example 2: Add New Data Field

**Step 1**: Identify field ID from form
```
Field 500: New Client Preference
```

**Step 2**: Add to extractor
```python
# src/processors/personal_information_extractor.py
new_field = safe_get(combined_data, "500", "")
add_if_value(main_personal_section, "preference", new_field)
```

**Step 3**: Test extraction
```bash
python3 -c "
from src.processors.personal_information_extractor import extract_personal_information
data = {'500': 'Test Value'}
result = extract_personal_information(data)
print(result)
"
```

---

### Example 3: Modify Field Mapping

**Current Approach**: Fallback chain
```python
# Try field 144, fallback to field 3
name = safe_get(data, "144", safe_get(data, "3", ""))
```

**To Add New Variation**:
```python
# Try field 144, then 3, then 200
name = safe_get(data, "144",
       safe_get(data, "3",
       safe_get(data, "200", "")))
```

---

## Testing & Validation

### Unit Testing

```python
# Test a extractor
from src.processors.personal_information_extractor import extract_personal_information

test_data = {
    "144": "John",
    "145": "Smith",
    "94": "1980-02-13",
    "6": "Engineer"
}

result = extract_personal_information(test_data)
assert result['client_name'] == "John Smith"
```

### Integration Testing

```bash
# 1. Start server
python3 src/webhook_server.py

# 2. Send test fact find
curl -X POST http://localhost:5001/ff \
  -H "Content-Type: application/json" \
  -d @test_fact_find.json

# 3. Send test automation form
curl -X POST http://localhost:5001/automation \
  -H "Content-Type: application/json" \
  -d @test_automation.json

# 4. Check status
curl http://localhost:5001/status
```

---

## Performance Considerations

### Data Size
- Fact find JSON: ~8-10 KB
- Automation form: ~3-5 KB
- Combined report: ~10-15 KB
- Zapier webhook payload: ~15-20 KB

### Processing Time
- Form reception: < 100ms
- Matching: < 50ms
- Extraction: < 200ms
- Zapier send: 200-500ms
- **Total**: ~1-2 seconds per submission

### Memory Usage
- Per form: ~1 MB
- Per webhook cycle: ~5-10 MB
- System baseline: ~30-50 MB

---

## Error Handling

### Common Errors

**1. Field Not Found**
```python
# Issue: Field returns empty string
# Solution: Add fallback field
name = safe_get(data, "144", safe_get(data, "3", "Unknown"))
```

**2. Type Mismatch**
```python
# Issue: Currency field is string with $
# Solution: Parse currency
amount = clean_currency(value)  # Returns float
```

**3. Missing Couple Data**
```python
# Issue: Partner fields empty but is_couple=True
# Solution: Check partner data before adding
if partner_full_name:
    result.update(partner_fields)
```

---

## Debugging

### Enable Debug Logging

```python
# In webhook_server.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run
python3 src/webhook_server.py
```

### Print Form Data

```python
# In extractor
import json
print("Input data:")
print(json.dumps(combined_data, indent=2))
```

### Check Field Values

```python
# Test specific field
from pathlib import Path
import json

with open("data/forms/fact_finds/email_date.json") as f:
    data = json.load(f)
    print(f"Field 144: {data.get('144')}")
    print(f"Field 145: {data.get('145')}")
```

---

## Security Considerations

1. **Email Validation**
   - Always validate email format before processing
   - Sanitize email for file paths (replace @ and .)

2. **Data Privacy**
   - Don't log sensitive information
   - Implement access controls for /status endpoint
   - Consider encrypting stored form data

3. **Input Validation**
   - Validate all form data before processing
   - Use safe_get() for field access
   - Handle unexpected data types

---

## Deployment Checklist

- [ ] Update configuration for Zapier webhook URL
- [ ] Set environment variables for credentials
- [ ] Create data/forms subdirectories
- [ ] Test with sample forms
- [ ] Verify Zapier webhook connectivity
- [ ] Configure logging and monitoring
- [ ] Set up backup for form storage
- [ ] Document custom field mappings
- [ ] Train users on form completion

---

## Version Control

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/add-travel-insurance

# Make changes, test
git add .
git commit -m "Add travel insurance generator"

# Push and create PR
git push origin feature/add-travel-insurance
```

### Commit Message Format
```
[TYPE] Brief description

Longer description if needed.

Fixes #123
```

Types: feat, fix, docs, refactor, test, chore

---

## Documentation Standards

1. **Function Documentation**
   ```python
   def extract_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
       """
       Brief description.

       Args:
           form_data: Input form data dictionary

       Returns:
           Dictionary with extracted data
       """
   ```

2. **Code Comments**
   ```python
   # Extract main contact needs
   main_needs = safe_get(form_data, '380', 0)
   ```

3. **API Documentation**
   - Update API_REFERENCE.md for endpoint changes
   - Include request/response examples
   - Document error codes

---

## Related Documentation

- `CHANGELOG.md` - Version history and updates
- `API_REFERENCE.md` - API endpoints and field mappings
- `field_mappings.yaml` - Form field configurations

---

## Support & Contact

For implementation questions or issues:
1. Check the documentation files
2. Review existing code examples
3. Check test cases for usage patterns
4. Contact development team

---

## Version Info
- **Last Updated**: 2025-11-01
- **Documentation Version**: 1.0
- **Status**: Production Ready
