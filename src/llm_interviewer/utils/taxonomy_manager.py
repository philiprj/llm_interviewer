import json
import os
from pathlib import Path
from typing import Any, Dict, List

from ..config.taxonomy import get_taxonomy_summary, load_taxonomy, validate_taxonomy


class TaxonomyManager:
    """Utility class for managing interview taxonomies"""

    def __init__(self, taxonomy_path: str = None):
        self.taxonomy_path = taxonomy_path
        self.taxonomy = load_taxonomy(taxonomy_path)

    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load taxonomy from a specific file"""
        return load_taxonomy(file_path)

    def save_taxonomy(self, taxonomy: Dict[str, Any], file_path: str):
        """Save taxonomy to a JSON file"""
        validate_taxonomy(taxonomy)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(taxonomy, f, indent=2, ensure_ascii=False)

    def add_domain(self, domain_name: str, subdomains: List[Dict] = None):
        """Add a new domain to the taxonomy"""
        new_domain = {"name": domain_name, "subdomains": subdomains or []}

        self.taxonomy["domains"].append(new_domain)
        return self.taxonomy

    def add_subdomain(self, domain_name: str, subdomain_data: Dict):
        """Add a subdomain to an existing domain"""
        for domain in self.taxonomy["domains"]:
            if domain["name"] == domain_name:
                if "subdomains" not in domain:
                    domain["subdomains"] = []
                domain["subdomains"].append(subdomain_data)
                return self.taxonomy

        raise ValueError(f"Domain '{domain_name}' not found")

    def remove_domain(self, domain_name: str):
        """Remove a domain from the taxonomy"""
        self.taxonomy["domains"] = [
            domain
            for domain in self.taxonomy["domains"]
            if domain["name"] != domain_name
        ]
        return self.taxonomy

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current taxonomy"""
        return get_taxonomy_summary(self.taxonomy)

    def list_domains(self) -> List[str]:
        """Get list of all domain names"""
        return [domain["name"] for domain in self.taxonomy["domains"]]

    def list_subdomains(self, domain_name: str) -> List[str]:
        """Get list of subdomain names for a specific domain"""
        for domain in self.taxonomy["domains"]:
            if domain["name"] == domain_name:
                return [subdomain["name"] for subdomain in domain.get("subdomains", [])]

        raise ValueError(f"Domain '{domain_name}' not found")

    def export_to_dict(self) -> Dict[str, Any]:
        """Export current taxonomy as dictionary"""
        return self.taxonomy.copy()

    def validate_current_taxonomy(self) -> bool:
        """Validate the current taxonomy structure"""
        return validate_taxonomy(self.taxonomy)
