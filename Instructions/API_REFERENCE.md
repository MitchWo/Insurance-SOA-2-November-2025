# Insurance SOA API Reference Guide

## Quick Start

### Server Status
```bash
curl http://localhost:5001/status
```

### Response Example:
```json
{
  "status": "running",
  "statistics": {
    "total_fact_finds": 5,
    "total_automation_forms": 3,
    "confident_matches": 0
  }
}
```

---

## API Endpoints

### 1. Form Submission Endpoints

#### Fact Find Form Submission
```
POST /ff
POST /webhook/fact-find
```

**Request Body**: Raw JSON from Gravity Forms
**Response**:
```json
{
  "status": "success",
  "form_type": "fact_find",
  "email": "user@example.com",
  "saved_to": "/path/to/file.json",
  "match_info": {},
  "zapier_triggered": true,
  "zapier_status": "success"
}
```

---

#### Automation Form Submission
```
POST /automation
POST /webhook/automation-form
```

**Request Body**: Raw JSON from Gravity Forms
**Response**:
```json
{
  "status": "success",
  "form_type": "automation_form",
  "email": "user@example.com",
  "saved_to": "/path/to/file.json",
  "match_info": {},
  "zapier_triggered": true,
  "zapier_status": "success"
}
```

---

### 2. Report Generation Endpoints

#### Scope of Advice
```
POST /generate/scope-of-advice
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "form_data": { ... }
}
```

**Response**:
```json
{
  "section_type": "scope_of_advice",
  "products_in_scope": ["Life Insurance"],
  "products_out_of_scope": ["Income Protection"],
  "sections": {
    "limitations": "Client has sufficient assets...",
    "form_submission_date": "Wednesday, 22 October 2025"
  }
}
```

---

#### Personal Information
```
POST /generate/personal-information
```

**Response**:
```json
{
  "section_type": "personal_information",
  "is_couple": false,
  "client_name": "John Smith",
  "client_age": "45",
  "client_occupation": "Manager",
  "client_email": "john@example.com",
  "employment_status": "Employed",
  "salary_before_tax": "100000"
}
```

---

#### Assets & Liabilities
```
POST /generate/assets-liabilities
```

**Response**:
```json
{
  "section_type": "assets_liabilities",
  "property_value": "500000",
  "property_mortgage": "300000",
  "property_equity": "200000",
  "kiwisaver_balance": "85000",
  "total_assets": "585000",
  "total_liabilities": "300000",
  "net_worth": "285000",
  "debt_to_asset_ratio": "51.3"
}
```

---

#### Life Insurance Fields
```
POST /generate/life-insurance-fields
```

**Response**:
```json
{
  "client_name": "John Smith",
  "is_couple": false,
  "main_debt_repayment": 300000,
  "main_replacement_income": 150000,
  "main_child_education": 50000,
  "main_final_expenses": 20000,
  "main_total_needs": 520000,
  "main_total_offsets": 200000,
  "main_net_coverage": 320000,
  "recommendation_status": "coverage_needed",
  "coverage_level": "moderate"
}
```

---

#### Trauma Insurance Fields
```
POST /generate/trauma-insurance-fields
```

---

#### Income Protection Fields
```
POST /generate/income-protection-fields
```

---

#### Health Insurance Fields
```
POST /generate/health-insurance-fields
```

---

#### Accidental Injury Fields
```
POST /generate/accidental-injury-fields
```

---

#### Combined Report
```
POST /generate/combined-report
```

**Response**: All sections combined into single report object

---

### 3. System Status Endpoints

#### Health Check
```
GET /health
```

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2025-11-01T12:30:45"
}
```

---

#### System Status
```
GET /status
```

**Response**:
```json
{
  "status": "running",
  "statistics": {
    "total_fact_finds": 5,
    "total_automation_forms": 3,
    "confident_matches": 0,
    "average_confidence": 0,
    "unmatched_fact_finds": 5,
    "unmatched_automation_forms": 3
  },
  "unmatched_automation_forms": 3,
  "unmatched_fact_finds": 5
}
```

---

#### Matches
```
GET /matches
```

**Response**:
```json
{
  "total_matches": 0,
  "confident_matches": 0,
  "matches": []
}
```

---

## Form Field Mappings

### Main Contact (Client) Fields

| Field ID | Description | Notes |
|----------|-------------|-------|
| 144 | First Name | Primary field for client first name |
| 145 | Last Name | Client last name |
| 94 | Date of Birth | Format: YYYY-MM-DD or MM/DD/YYYY |
| 6 | Occupation | Client's occupation |
| 276 | Self-Employed Flag | "Yes"/"No" to determine if self-employed |
| 277 | Employer Name | Employer's name if not self-employed |
| 278 | Hours Per Week | Employment hours |
| 279 | Salary/Income | Annual income before tax |
| 10 | Annual Income (Alt) | Fallback income field |
| 220 | Phone Number | Contact phone |
| 219 | Email Address (Alt) | Alternative email field |
| 26 | Will Status | "Yes"/"No" for will/EPA in place |

### Partner Fields (if couple)

| Field ID | Description | Notes |
|----------|-------------|-------|
| 146 | Partner First Name | Primary field for partner first name |
| 147 | Partner Last Name | Partner last name |
| 95 | Partner DOB | Partner's date of birth |
| 286 | Partner Occupation | Partner's occupation |
| 483 | Partner Self-Employed | "Yes"/"No" flag |
| 288 | Partner Employer | Partner's employer name |
| 296 | Partner Salary | Partner's annual income |
| 252 | Partner Smoker | "Yes"/"No" smoker status |
| 300 | Partner Will Status | Partner's will/EPA status |

### Life Insurance Needs Analysis Fields

#### Main Contact

| Field ID | Description | Amount Type |
|----------|-------------|--------------|
| 380 | Debt Repayment | Currency |
| 381 | Replacement Income | Currency |
| 382 | Child Education | Currency |
| 383 | Final Expenses | Currency |
| 384 | Other Considerations | Currency |
| 386 | Assets Offset | Currency |
| 388 | KiwiSaver Offset | Currency |

#### Partner

| Field ID | Description | Amount Type |
|----------|-------------|--------------|
| 391 | Partner Debt Repayment | Currency |
| 392 | Partner Replacement Income | Currency |
| 393 | Partner Child Education | Currency |
| 394 | Partner Final Expenses | Currency |
| 395 | Partner Other Considerations | Currency |
| 397 | Partner Assets Offset | Currency |
| 399 | Partner KiwiSaver Offset | Currency |

### KiwiSaver Account Fields (Multiple Variations)

#### Standard Set 1
| Field ID | Description |
|----------|-------------|
| 60 | Provider |
| 61 | Fund Type |
| 62 | Balance |

#### Standard Set 2
| Field ID | Description |
|----------|-------------|
| 63 | Provider |
| 64 | Fund Type |
| 65 | Balance |

#### Alternative Set (New Forms)
| Field ID | Description |
|----------|-------------|
| 380-382 | Accounts 1 (provider, fund, balance) |
| 383-385 | Account 2 |
| 386-388 | Account 3 |
| 391-393 | Account 4 |
| 394-396 | Account 5 |
| 397-399 | Account 6 |

### Property & Asset Fields

| Field ID | Description | Notes |
|----------|-------------|-------|
| 15 | Current House Value | Property valuation |
| 16 | Current House Address | Property address |
| 17 | Current Mortgage | Mortgage balance |
| 33 | Asset 1 Name | Asset type |
| 26 | Asset 1 Value | Asset value |
| 19 | Asset 2 Name | Business valuation, etc. |
| 36 | Asset 2 Value | Asset value |

### Scope of Advice Fields

| Field ID | Description | Type |
|----------|-------------|------|
| 5 | Main Scope Field | Checkbox group |
| 5.1 | Life Insurance | Checkbox |
| 5.2 | Income Protection | Checkbox |
| 5.3 | Trauma Cover | Checkbox |
| 5.4 | Health Insurance | Checkbox |
| 5.5 | Total & Permanent Disability | Checkbox |
| 5.6 | ACC Top-Up | Checkbox |
| 6 | Main Limitations Field | Checkbox group |
| 6.1 | Employer Medical | Checkbox |
| 6.2 | Strong Assets | Checkbox |
| 6.3 | Budget Limitations | Checkbox |
| 6.4 | Self-Insure | Checkbox |
| 6.5 | No Dependants | Checkbox |
| 6.6 | Uninsurable Occupation | Checkbox |
| 6.7 | Other | Checkbox |
| 7 | Limitation Notes | Text field |

### Data Quality Fields

| Field ID | Description | Source |
|----------|-------------|--------|
| date_created | Form Submission Date | WordPress/Gravity Forms |
| email | Contact Email | Form submission |
| ip | IP Address | Form submission |
| user_agent | Browser Info | Form submission |

---

## Data Type Conversions

### Currency Fields
- Stored as strings with $ and commas
- Automatically converted to float
- Zero values are treated as 0.0
- Empty strings converted to 0.0

### Date Fields
- Input format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS"
- Output format for Zapier: "Day, DD Month YYYY"
- Example: "2025-10-30 01:13:38" → "Thursday, 30 October 2025"

### Checkbox Fields
- Recognized values: 'yes', 'true', '1', 'checked', 'on', 'x'
- Product names treated as selected (e.g., 'Life Insurance')
- Empty string or None = unchecked

### Calculated Fields
All calculated fields are derived automatically:
- `total_needs`: Sum of all needs
- `total_offsets`: Sum of all offsets
- `net_coverage`: total_needs - total_offsets (minimum 0)
- `total_assets`: Sum of all assets
- `net_worth`: total_assets - total_liabilities
- `debt_to_asset_ratio`: (total_liabilities / total_assets) * 100

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "No data received",
  "status": 400
}
```

### 500 Internal Server Error
```json
{
  "error": "Error processing form: [details]",
  "status": 500
}
```

---

## Zapier Integration

### Webhook URL
```
https://hooks.zapier.com/hooks/catch/12679562/urq5tjh/
```

### Payload Structure
The system flattens nested JSON and sends:
- All personal information fields
- All asset/liability fields
- All insurance recommendation fields
- Scope of advice details
- System metadata (status, confidence, etc.)

### Success Criteria
- HTTP 200 response
- Retry logic: 3 attempts with exponential backoff
- All data received in Zapier

---

## Example Workflows

### Complete Client Processing

1. **Fact Find Submission**
   ```bash
   curl -X POST http://localhost:5001/ff \
     -H "Content-Type: application/json" \
     -d @fact_find.json
   ```

2. **Automation Form Submission**
   ```bash
   curl -X POST http://localhost:5001/automation \
     -H "Content-Type: application/json" \
     -d @automation.json
   ```

3. **Generate Combined Report** (Automatic)
   - System automatically matches forms
   - Generates all sections
   - Sends to Zapier webhook

4. **Check Status**
   ```bash
   curl http://localhost:5001/status
   ```

---

## Best Practices

1. **Email Consistency**: Ensure email addresses match between fact find and automation form
2. **Date Format**: Use ISO 8601 format (YYYY-MM-DD) for dates
3. **Currency Format**: Remove $ and commas from currency values before submission
4. **Validation**: Always check /status endpoint to verify forms loaded
5. **Monitoring**: Monitor Zapier logs to confirm webhook receipt

---

## Support & Debugging

### Check Form Loading
```bash
curl http://localhost:5001/status | jq '.statistics'
```

### Find Specific Email
```bash
ls data/forms/fact_finds/ | grep email_pattern
ls data/forms/automation_forms/ | grep email_pattern
```

### View Raw Form Data
```bash
cat data/forms/fact_finds/email_date.json | jq '.'
```

### Test Zapier Webhook Locally
```bash
python3 -c "
from src.processors.zapier_trigger import ZapierTrigger
z = ZapierTrigger()
result = z.trigger({'test': 'data'})
print(result)
"
```

---

## Version Info
- **API Version**: 1.0.1
- **Last Updated**: 2025-11-01
- **Status**: Production Ready
