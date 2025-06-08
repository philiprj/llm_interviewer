import json
import os
from pathlib import Path
from typing import Any, Dict


def load_taxonomy(taxonomy_path: str | None = None) -> Dict[str, Any]:
    """Load taxonomy from JSON file"""

    if taxonomy_path is None:
        # Default to the taxonomy file in the same directory
        current_dir = Path(
            __file__
        ).parent.parent.parent.parent  # Go up to workspace root
        taxonomy_path = current_dir / "data" / "interview_taxonomy.json"

    try:
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Taxonomy file not found at {taxonomy_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in taxonomy file: {e}")


def validate_taxonomy(taxonomy: Dict[str, Any]) -> bool:
    """Validate taxonomy structure"""

    required_keys = ["domains"]

    if not isinstance(taxonomy, dict):
        raise ValueError("Taxonomy must be a dictionary")

    for key in required_keys:
        if key not in taxonomy:
            raise ValueError(f"Missing required key: {key}")

    if not isinstance(taxonomy["domains"], list):
        raise ValueError("'domains' must be a list")

    for domain in taxonomy["domains"]:
        if not isinstance(domain, dict) or "name" not in domain:
            raise ValueError("Each domain must have a 'name' field")

        if "subdomains" in domain:
            if not isinstance(domain["subdomains"], list):
                raise ValueError("'subdomains' must be a list")

            for subdomain in domain["subdomains"]:
                if not isinstance(subdomain, dict) or "name" not in subdomain:
                    raise ValueError("Each subdomain must have a 'name' field")

    return True


def get_taxonomy_summary(taxonomy: Dict[str, Any]) -> Dict[str, Any]:
    """Get a summary of the taxonomy structure"""

    summary = {"total_domains": len(taxonomy["domains"]), "domains": []}

    for domain in taxonomy["domains"]:
        domain_info = {
            "name": domain["name"],
            "subdomains_count": len(domain.get("subdomains", [])),
            "subdomains": [],
        }

        for subdomain in domain.get("subdomains", []):
            subdomain_info = {
                "name": subdomain["name"],
                "skills_count": len(subdomain.get("core_skills", [])),
            }
            domain_info["subdomains"].append(subdomain_info)

        summary["domains"].append(domain_info)

    return summary


# Load the default taxonomy
try:
    INTERVIEW_DOMAINS = load_taxonomy()
    validate_taxonomy(INTERVIEW_DOMAINS)
except Exception as e:
    print(f"Warning: Could not load taxonomy: {e}")
    # Fallback to empty structure
    INTERVIEW_DOMAINS = {"domains": []}
