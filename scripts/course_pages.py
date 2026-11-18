"""Compatibility facade delegating structured course loading and building to roadmap.courses."""
from roadmap.courses import build_courses as build, load_courses as load

__all__ = ['build', 'load']
