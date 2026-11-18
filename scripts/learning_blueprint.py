"""Compatibility facade delegating competency blueprint checks to roadmap.audit_pages."""
from roadmap.audit_pages import (
    PLAN,
    VALID_STATUS,
    build_blueprint as build,
    inventory,
    validate_plan,
    verified_assessment_links,
)

__all__ = ['PLAN', 'VALID_STATUS', 'build', 'inventory', 'validate_plan', 'verified_assessment_links']
