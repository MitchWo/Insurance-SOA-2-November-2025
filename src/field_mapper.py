"""
Field Mapper for Gravity Forms to Fact Find Data
Maps Gravity Forms field IDs to semantic field names
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union


class FieldMapper:
    """
    Maps Gravity Forms field IDs to semantic field names
    Handles both "f" prefixed keys (f144) and plain keys (144)
    """

    def __init__(self, config_path: str = "config/field_mappings.yaml"):
        """
        Initialize the field mapper with a configuration file

        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self.mappings = {}
        self.reverse_mappings = {}  # field_id -> (category, field_name)
        self.load_mappings()

    def load_mappings(self):
        """Load field mappings from the YAML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self.mappings = yaml.safe_load(f)

        # Build reverse mappings for efficient lookups
        self._build_reverse_mappings()

    def _build_reverse_mappings(self):
        """Build reverse mappings from field IDs to category/field names"""
        self.reverse_mappings = {}

        for category, fields in self.mappings.items():
            if isinstance(fields, dict):
                for field_name, field_ids in fields.items():
                    if isinstance(field_ids, list):
                        for field_id in field_ids:
                            if field_id:  # Skip empty field IDs
                                self.reverse_mappings[str(field_id)] = (category, field_name)

    def get_field(self, data: Dict[str, Any], category: str, field_name: str) -> Optional[Any]:
        """
        Extract a field value from raw data using the mapping

        Args:
            data: Raw data dictionary (typically from Gravity Forms)
            category: Category name (e.g., 'client', 'partner', 'assets')
            field_name: Field name within the category (e.g., 'first_name', 'annual_income')

        Returns:
            Field value if found, None otherwise
        """
        # Check if category exists
        if category not in self.mappings:
            return None

        # Check if field exists in category
        category_fields = self.mappings.get(category, {})
        if field_name not in category_fields:
            return None

        # Get field IDs for this field
        field_ids = category_fields[field_name]
        if not isinstance(field_ids, list):
            return None

        # Try to find the field value in the data
        for field_id in field_ids:
            if not field_id:  # Skip empty field IDs
                continue

            field_id_str = str(field_id)

            # Try with "f" prefix
            f_key = f"f{field_id_str}"
            if f_key in data:
                return data[f_key]

            # Try without prefix
            if field_id_str in data:
                return data[field_id_str]

            # Try as integer key
            try:
                field_id_int = int(field_id_str)
                if field_id_int in data:
                    return data[field_id_int]
            except (ValueError, TypeError):
                pass

        return None

    def get_category_fields(self, category: str) -> Dict[str, List[int]]:
        """
        Get all field mappings for a category

        Args:
            category: Category name

        Returns:
            Dictionary of field names to field IDs
        """
        return self.mappings.get(category, {})

    def get_all_categories(self) -> List[str]:
        """Get list of all available categories"""
        return list(self.mappings.keys())

    def get_field_count(self, category: Optional[str] = None) -> int:
        """
        Get count of fields in a category or total fields

        Args:
            category: Optional category name. If None, returns total count

        Returns:
            Number of fields
        """
        if category:
            category_fields = self.mappings.get(category, {})
            return len(category_fields)
        else:
            total = 0
            for cat_fields in self.mappings.values():
                if isinstance(cat_fields, dict):
                    total += len(cat_fields)
            return total

    def extract_category(self, data: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Extract all fields in a category from the raw data

        Args:
            data: Raw data dictionary
            category: Category name

        Returns:
            Dictionary with field names as keys and extracted values
        """
        result = {}
        category_fields = self.mappings.get(category, {})

        for field_name in category_fields:
            value = self.get_field(data, category, field_name)
            if value is not None:
                result[field_name] = value

        return result

    def extract_all(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract all mapped fields from the raw data

        Args:
            data: Raw data dictionary

        Returns:
            Nested dictionary with categories as keys
        """
        result = {}
        for category in self.get_all_categories():
            extracted = self.extract_category(data, category)
            if extracted:  # Only include categories with data
                result[category] = extracted

        return result

    def describe_field(self, field_id: Union[str, int]) -> Optional[Dict[str, str]]:
        """
        Get information about a field ID

        Args:
            field_id: Field ID to look up

        Returns:
            Dictionary with category and field_name, or None if not found
        """
        field_id_str = str(field_id)

        # Check reverse mapping
        if field_id_str in self.reverse_mappings:
            category, field_name = self.reverse_mappings[field_id_str]
            return {
                'field_id': field_id_str,
                'category': category,
                'field_name': field_name
            }

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the field mappings

        Returns:
            Dictionary with mapping statistics
        """
        stats = {
            'total_categories': len(self.get_all_categories()),
            'total_fields': self.get_field_count(),
            'categories': {}
        }

        for category in self.get_all_categories():
            stats['categories'][category] = {
                'field_count': self.get_field_count(category),
                'fields': list(self.get_category_fields(category).keys())
            }

        return stats

    def __repr__(self) -> str:
        """String representation of the FieldMapper"""
        return f"FieldMapper(categories={len(self.get_all_categories())}, total_fields={self.get_field_count()})"