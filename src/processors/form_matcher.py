"""
Form Matcher
Intelligently matches FactFind forms with AutomationForms based on email and other criteria
"""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.fact_find import FactFind
from models.automation_form import AutomationForm


class MatchResult:
    """Represents the result of a form matching attempt"""

    def __init__(self, fact_find: FactFind, automation_form: AutomationForm, confidence: float, reasons: List[str]):
        self.fact_find = fact_find
        self.automation_form = automation_form
        self.confidence = confidence  # 0.0 to 1.0
        self.reasons = reasons  # List of reasons for the match
        self.matched_at = datetime.now()

    def is_confident_match(self, threshold: float = 0.8) -> bool:
        """Check if confidence exceeds threshold"""
        return self.confidence >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert match result to dictionary"""
        return {
            'confidence': self.confidence,
            'is_confident': self.is_confident_match(),
            'reasons': self.reasons,
            'matched_at': self.matched_at.isoformat(),
            'fact_find_case_id': self.fact_find.case_info.get('case_id'),
            'automation_form_email': self.automation_form.client_details.get('email')
        }

    def __str__(self) -> str:
        return f"MatchResult(confidence={self.confidence:.2f}, reasons={len(self.reasons)})"


class FormMatcher:
    """
    Matches FactFind forms with AutomationForms using multiple criteria
    """

    def __init__(self, storage_dir: str = "data/forms"):
        """
        Initialize the form matcher

        Args:
            storage_dir: Directory to store form data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage for loaded forms
        self.fact_finds: Dict[str, FactFind] = {}  # Key: case_id or email
        self.automation_forms: Dict[str, AutomationForm] = {}  # Key: email

        # Matching history
        self.match_history: List[MatchResult] = []

    def add_fact_find(self, fact_find: FactFind, identifier: Optional[str] = None) -> str:
        """
        Add a fact find to the matcher

        Args:
            fact_find: FactFind instance
            identifier: Optional identifier (defaults to case_id or email)

        Returns:
            Identifier used to store the fact find
        """
        if not identifier:
            identifier = fact_find.case_info.get('case_id') or fact_find.client_info.get('email')

        if not identifier:
            raise ValueError("Cannot add fact find without case_id or email")

        self.fact_finds[identifier] = fact_find

        # Also store by email for easy lookup
        email = fact_find.client_info.get('email')
        if email and email != identifier:
            self.fact_finds[email] = fact_find

        return identifier

    def add_automation_form(self, automation_form: AutomationForm, identifier: Optional[str] = None) -> str:
        """
        Add an automation form to the matcher

        Args:
            automation_form: AutomationForm instance
            identifier: Optional identifier (defaults to email)

        Returns:
            Identifier used to store the automation form
        """
        if not identifier:
            identifier = automation_form.client_details.get('email')

        if not identifier:
            raise ValueError("Cannot add automation form without email")

        self.automation_forms[identifier] = automation_form
        return identifier

    def match_by_email(self, email: str) -> Optional[MatchResult]:
        """
        Find matching forms by email address

        Args:
            email: Email address to match

        Returns:
            MatchResult if both forms found, None otherwise
        """
        email = email.lower().strip()

        # Find fact find with this email
        fact_find = self.fact_finds.get(email)
        if not fact_find:
            # Try to find by searching through all fact finds
            for ff in self.fact_finds.values():
                if ff.client_info.get('email', '').lower().strip() == email:
                    fact_find = ff
                    break

        # Find automation form with this email
        automation_form = self.automation_forms.get(email)
        if not automation_form:
            # Try to find by searching through all automation forms
            for af in self.automation_forms.values():
                if af.client_details.get('email', '').lower().strip() == email:
                    automation_form = af
                    break

        if not fact_find or not automation_form:
            return None

        # Calculate match confidence
        confidence, reasons = self._calculate_match_confidence(fact_find, automation_form)

        match_result = MatchResult(fact_find, automation_form, confidence, reasons)
        self.match_history.append(match_result)

        return match_result

    def find_best_match(self, automation_form: AutomationForm) -> Optional[MatchResult]:
        """
        Find the best matching fact find for an automation form

        Args:
            automation_form: AutomationForm to match

        Returns:
            MatchResult with highest confidence, or None
        """
        email = automation_form.client_details.get('email', '').lower().strip()

        if not email:
            return None

        # First try direct email match
        direct_match = self.match_by_email(email)
        if direct_match and direct_match.is_confident_match():
            return direct_match

        # If no confident direct match, try all fact finds
        best_match = None
        best_confidence = 0.0

        for fact_find in self.fact_finds.values():
            confidence, reasons = self._calculate_match_confidence(fact_find, automation_form)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = MatchResult(fact_find, automation_form, confidence, reasons)

        if best_match:
            self.match_history.append(best_match)

        return best_match

    def _calculate_match_confidence(self, fact_find: FactFind, automation_form: AutomationForm) -> Tuple[float, List[str]]:
        """
        Calculate match confidence between a fact find and automation form

        Args:
            fact_find: FactFind instance
            automation_form: AutomationForm instance

        Returns:
            Tuple of (confidence score 0-1, list of matching reasons)
        """
        confidence = 0.0
        reasons = []

        # Email match (most important - 50% weight)
        ff_email = fact_find.client_info.get('email', '').lower().strip()
        af_email = automation_form.client_details.get('email', '').lower().strip()

        if ff_email and af_email and ff_email == af_email:
            confidence += 0.5
            reasons.append(f"Email match: {ff_email}")
        elif ff_email and af_email:
            reasons.append(f"Email mismatch: {ff_email} vs {af_email}")
            return 0.0, reasons  # Email mismatch is disqualifying

        # Couple status match (20% weight)
        if fact_find.is_couple() == automation_form.is_couple():
            confidence += 0.2
            status = "couple" if fact_find.is_couple() else "single"
            reasons.append(f"Couple status match: {status}")
        else:
            reasons.append("Couple status mismatch")

        # Case ID match if available (10% weight)
        case_id = fact_find.case_info.get('case_id')
        if case_id:
            confidence += 0.1
            reasons.append(f"Case ID present: {case_id}")

        # Timing proximity (10% weight) - forms submitted within reasonable timeframe
        ff_date_str = fact_find.case_info.get('form_date')
        af_date_str = automation_form.additional.get('recommendation_date')

        if ff_date_str and af_date_str:
            try:
                ff_date = datetime.fromisoformat(ff_date_str.replace('Z', '+00:00'))
                af_date = datetime.fromisoformat(af_date_str.replace('Z', '+00:00'))

                time_diff = abs((af_date - ff_date).total_seconds())
                days_diff = time_diff / 86400

                if days_diff <= 7:  # Within a week
                    confidence += 0.1
                    reasons.append(f"Forms submitted {days_diff:.1f} days apart")
                elif days_diff <= 30:  # Within a month
                    confidence += 0.05
                    reasons.append(f"Forms submitted {days_diff:.1f} days apart (acceptable)")
                else:
                    reasons.append(f"Forms submitted {days_diff:.1f} days apart (concerning)")
            except (ValueError, AttributeError):
                pass

        # Existing insurance consistency check (10% weight)
        if self._check_insurance_consistency(fact_find, automation_form):
            confidence += 0.1
            reasons.append("Existing insurance details consistent")

        return min(confidence, 1.0), reasons

    def _check_insurance_consistency(self, fact_find: FactFind, automation_form: AutomationForm) -> bool:
        """
        Check if existing insurance details are consistent between forms

        Args:
            fact_find: FactFind instance
            automation_form: AutomationForm instance

        Returns:
            True if consistent, False otherwise
        """
        # Compare life cover amounts
        ff_life = fact_find.existing_insurance_main.get('life_cover_amount')
        af_life = automation_form.main_existing_cover.get('life_amount')

        if ff_life and af_life:
            # Allow 5% difference to account for rounding
            if abs(ff_life - af_life) / max(ff_life, af_life) <= 0.05:
                return True

        # Compare providers
        ff_life_provider = fact_find.existing_insurance_main.get('life_cover_provider', '').lower()
        af_life_provider = automation_form.main_existing_cover.get('life_provider', '').lower()

        if ff_life_provider and af_life_provider:
            if ff_life_provider in af_life_provider or af_life_provider in ff_life_provider:
                return True

        # If we can't verify, return True (benefit of doubt)
        return not (ff_life or af_life or ff_life_provider or af_life_provider)

    def get_unmatched_fact_finds(self) -> List[FactFind]:
        """Get list of fact finds that haven't been matched yet"""
        matched_emails = {match.fact_find.client_info.get('email') for match in self.match_history}

        unmatched = []
        for fact_find in self.fact_finds.values():
            email = fact_find.client_info.get('email')
            if email not in matched_emails:
                unmatched.append(fact_find)

        return unmatched

    def get_unmatched_automation_forms(self) -> List[AutomationForm]:
        """Get list of automation forms that haven't been matched yet"""
        matched_emails = {match.automation_form.client_details.get('email') for match in self.match_history}

        unmatched = []
        for automation_form in self.automation_forms.values():
            email = automation_form.client_details.get('email')
            if email not in matched_emails:
                unmatched.append(automation_form)

        return unmatched

    def save_match_history(self, filepath: str = "data/match_history.json"):
        """Save match history to file"""
        history_data = [match.to_dict() for match in self.match_history]

        output_file = Path(filepath)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(history_data, f, indent=2, default=str)

    def get_match_statistics(self) -> Dict[str, Any]:
        """Get statistics about matching performance"""
        total_matches = len(self.match_history)
        confident_matches = sum(1 for m in self.match_history if m.is_confident_match())

        avg_confidence = sum(m.confidence for m in self.match_history) / total_matches if total_matches > 0 else 0

        return {
            'total_fact_finds': len(set(self.fact_finds.values())),
            'total_automation_forms': len(set(self.automation_forms.values())),
            'total_matches': total_matches,
            'confident_matches': confident_matches,
            'average_confidence': avg_confidence,
            'unmatched_fact_finds': len(self.get_unmatched_fact_finds()),
            'unmatched_automation_forms': len(self.get_unmatched_automation_forms())
        }

    def __str__(self) -> str:
        stats = self.get_match_statistics()
        return f"FormMatcher(fact_finds={stats['total_fact_finds']}, automation_forms={stats['total_automation_forms']}, matches={stats['total_matches']})"