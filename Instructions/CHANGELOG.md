# Insurance SOA System - Changelog

## Overview
This document tracks all significant changes, updates, and improvements made to the Insurance Statement of Advice (SOA) system.

---

## November 1, 2025 - Recent Updates

### 1. Form Submission Date Feature
**File**: `src/processors/scope_of_advice_generator.py`

#### Changes:
- Added `_extract_and_format_date()` method to extract and format the WordPress form submission date
- Extracts `date_created` field from raw form data (format: "YYYY-MM-DD HH:MM:SS")
- Formats date as "Day, DD Month YYYY" (e.g., "Wednesday, 22 October 2025")
- Date is now included in the scope of advice section under `sections.form_submission_date`

#### Implementation:
```python
@classmethod
def _extract_and_format_date(cls, data: Dict[str, Any]) -> Optional[str]:
    """Extract date_created from form data and format as 'Day, DD Month YYYY'"""
    date_str = data.get('date_created')
    if not date_str:
        return None
    try:
        dt = datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%A, %d %B %Y")
    except (ValueError, TypeError):
        return None
```

#### Usage:
The date is automatically extracted and included in the scope of advice JSON when generating reports.

---

### 2. Scope of Advice JSON Structure

**File**: `src/processors/scope_of_advice_generator.py`

#### Current Output Structure:
```json
{
  "section_type": "scope_of_advice",
  "products_in_scope": ["Life Insurance", "Total Permanent Disability (TPD)"],
  "products_out_of_scope": ["Income Protection", "Trauma Cover", "Health Insurance", "ACC Top-Up"],
  "sections": {
    "limitations": "Client has sufficient assets to self-insure risks",
    "form_submission_date": "Thursday, 30 October 2025"
  }
}
```

---

### 3. Checkbox Value Detection Enhancement

**File**: `src/processors/scope_of_advice_generator.py`

#### Changes:
- Updated `_is_checked()` method to recognize multiple checkbox value formats
- Now handles:
  - Explicit markers: 'yes', 'true', '1', 'checked', 'on', 'x'
  - Product names stored as values: 'Life Insurance', 'Total & Permanent Disability'
  - Any non-empty string is treated as checked

#### Implementation:
```python
@classmethod
def _is_checked(cls, value: Any) -> bool:
    """Convert various checkbox representations to boolean"""
    if value is None or value == "":
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ['yes', 'true', '1', 'checked', 'on', 'x']:
            return True
        return len(value_lower) > 0
    return bool(value)
```

---

### 4. Field Mapping Updates

**File**: `src/processors/personal_information_extractor.py` and `src/processors/assets_liabilities_extractor.py`

#### Key Mappings:
- **First Name**: Field 144 (fallback to 3)
- **Last Name**: Field 145
- **Date of Birth**: Field 94 (fallback to 95)
- **Occupation**: Field 6
- **Employer (Self-Employed)**: Field 276 (check for self-employed status)
- **Employer Name**: Field 277
- **Phone**: Field 220 (corrected from 219)
- **Will Status**: Field 26

#### Partner Fields:
- **Partner First Name**: Field 146
- **Partner Last Name**: Field 147
- **Partner DOB**: Field 95
- **Partner Occupation**: Field 286

#### KiwiSaver Fields (Multiple Variations Supported):
- Standard: Fields 60-65, 215-217, 222-226, 329
- Alternative: Fields 380-399 (for newer form versions)

---

### 5. Life Insurance Fields Extractor

**File**: `src/generators/life_insurance_fields.py`

#### Current Structure:
Extracts life insurance needs analysis with support for:
- **Main Contact**:
  - Debt Repayment (Field 380)
  - Replacement Income (Field 381)
  - Child Education (Field 382)
  - Final Expenses (Field 383)
  - Other Considerations (Field 384)
  - Assets Offset (Field 386)
  - KiwiSaver Offset (Field 388)

- **Partner** (if couple):
  - Debt Repayment (Field 391)
  - Replacement Income (Field 392)
  - Child Education (Field 393)
  - Final Expenses (Field 394)
  - Other Considerations (Field 395)
  - Assets Offset (Field 397)
  - KiwiSaver Offset (Field 399)

#### Output:
```json
{
  "client_name": "Test Client",
  "is_couple": false,
  "main_debt_repayment": 100000.0,
  "main_replacement_income": 60000.0,
  "main_child_education": 45000.0,
  "main_final_expenses": 10000.0,
  "main_other_considerations": 10000.0,
  "main_assets": 0.0,
  "main_kiwisaver": 100000.0,
  "main_total_needs": 225000.0,
  "main_total_offsets": 100000.0,
  "main_net_coverage": 125000.0,
  "main_needs_insurance": true,
  "recommendation_status": "coverage_needed",
  "coverage_level": "basic"
}
```

---

### 6. Auto Matcher - Data Loading Fix

**File**: `src/processors/auto_matcher.py`

#### Critical Fix:
- Changed from loading model-converted nested data to loading raw form JSON files
- Raw form JSON preserves flat field structure (Field 144, 145, etc.)
- Model `to_dict()` method was converting to nested structure which extractors couldn't process

#### Implementation:
```python
# Load raw fact find data from file
safe_email = email.replace('@', '_at_').replace('.', '_')
fact_find_files = list((forms_dir / "fact_finds").glob(f"{safe_email}_*.json"))
if fact_find_files:
    fact_find_files.sort(reverse=True)
    with open(fact_find_files[0]) as f:
        combined_data.update(json.load(f))
```

#### Impact:
- Extractors now receive data in expected format
- All field mappings work correctly
- Data flows properly to Zapier

---

### 7. Personal Information Extractor

**File**: `src/processors/personal_information_extractor.py`

#### Current Implementation:
Extracts personal information for both main contact and partner (if couple):

```json
{
  "section_type": "personal_information",
  "is_couple": false,
  "client_name": "Test Client",
  "client_age": "31",
  "client_occupation": "Test",
  "client_email": "test@test.com",
  "client_phone": "No",
  "employment_status": "Employed",
  "salary_before_tax": "0",
  "total_income": "0.0",
  "total_assets": "221000.0",
  "total_liabilities": "0.0",
  "net_worth": "221000.0",
  "number_of_children": 0,
  "partner_name": "TestPartner TestPartner last name",
  "partner_age": "31",
  "partner_occupation": "No",
  "partner_employment_status": "Employed",
  "partner_salary_before_tax": "0"
}
```

---

### 8. Assets & Liabilities Extractor

**File**: `src/processors/assets_liabilities_extractor.py`

#### Current Implementation:
Extracts financial assets and liabilities in lean format for Zapier:

```json
{
  "section_type": "assets_liabilities",
  "property_value": "0",
  "property_address": "",
  "property_mortgage": "0",
  "property_equity": "0",
  "kiwisaver_balance": "100000.0",
  "kiwisaver_count": 1,
  "other_assets_value": "0",
  "other_assets_count": 0,
  "total_liabilities": "0",
  "liability_count": 0,
  "total_assets": "100000.0",
  "net_worth": "100000.0",
  "debt_to_asset_ratio": "0.0"
}
```

#### Features:
- Supports multiple property fields
- KiwiSaver extraction with fallback field variations
- Flexible asset and liability field mapping
- Calculated financial metrics

---

### 9. Zapier Integration

**File**: `src/processors/zapier_trigger.py`

#### Webhook Configuration:
- **URL**: https://hooks.zapier.com/hooks/catch/12679562/urq5tjh/
- **Method**: POST
- **Retry Logic**: 3 attempts with exponential backoff
- **Data Format**: Flattened JSON structure
- **Success Response**: HTTP 200

#### Data Flattening:
- Nested structures converted to flat key-value pairs
- Table format for personal_information and assets_liabilities sections
- All data fields passed as Zapier variables

---

## Testing & Validation

### Test Cases Verified:
1. ✅ test@test.com - Single client with full data
2. ✅ dan@icreatebuilding.nz - Couple scenario with partial data
3. ✅ Date formatting - Multiple date formats verified
4. ✅ Scope of advice - Product selection and limitations
5. ✅ Zapier webhook - HTTP 200 success confirmation

### Known Issues Resolved:
- ✅ Field mapping mismatches across different form versions
- ✅ Model data vs raw form data format conflict
- ✅ Checkbox value format variance
- ✅ Date extraction and formatting
- ✅ Zero/empty value handling in extractors

---

## File Structure

```
Insurance-SOA-main/
├── src/
│   ├── processors/
│   │   ├── scope_of_advice_generator.py (Date feature added)
│   │   ├── personal_information_extractor.py (Field mappings)
│   │   ├── assets_liabilities_extractor.py (KiwiSaver support)
│   │   ├── auto_matcher.py (Raw JSON loading)
│   │   └── zapier_trigger.py (Webhook integration)
│   ├── generators/
│   │   ├── life_insurance_fields.py
│   │   ├── trauma_insurance_fields.py
│   │   ├── income_protection_fields.py
│   │   ├── health_insurance_fields.py
│   │   └── accidental_injury_fields.py
│   ├── models/
│   │   ├── fact_find.py
│   │   └── automation_form.py
│   └── webhook_server.py
├── data/
│   └── forms/
│       ├── fact_finds/ (Raw JSON submissions)
│       └── automation_forms/ (Raw JSON submissions)
└── config/
    └── field_mappings.yaml (Field reference)
```

---

## API Endpoints

### Fact Find Submission
```
POST /ff
POST /webhook/fact-find
```

### Automation Form Submission
```
POST /automation
POST /webhook/automation-form
```

### Report Generation
```
POST /generate/scope-of-advice
POST /generate/personal-information
POST /generate/assets-liabilities
POST /generate/combined-report
POST /generate/life-insurance-fields
POST /generate/trauma-insurance-fields
POST /generate/income-protection-fields
POST /generate/health-insurance-fields
POST /generate/accidental-injury-fields
```

### System Status
```
GET /status
GET /health
GET /matches
```

---

## Next Steps & Recommendations

### Planned Enhancements:
1. **Personal Information Section** - Organize into subsections (client contact, partner contact, employment, will status)
2. **Life Insurance Section** - Remove `needs_analysis_notes` from Zapier output, add filtering for zero/empty values
3. **Dynamic Field Extraction** - Implement configuration-based field mapping from field_mappings.yaml
4. **Error Handling** - Enhanced validation and user feedback for incomplete forms
5. **Audit Trail** - Track all webhooks sent to Zapier with timestamps

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.1 | 2025-11-01 | Added form submission date, enhanced checkbox detection |
| 1.0.0 | 2025-10-30 | Initial release with Zapier integration |

---

## Support & Troubleshooting

### Common Issues:

**Issue**: Forms not loading at webhook server startup
- **Solution**: Ensure JSON files are in correct directories with proper naming: `{email}_YYYYMMDD_HHMMSS.json`

**Issue**: Field values not populating
- **Solution**: Check field mappings - try alternative field IDs in fallback chain

**Issue**: Zero values showing in output
- **Solution**: Planned feature to exclude zero/empty values from Zapier output

**Issue**: Date not formatting correctly
- **Solution**: Verify WordPress date format is "YYYY-MM-DD HH:MM:SS"

---

## Contact & Questions
For questions about these changes, refer to the implementation files or contact the development team.
