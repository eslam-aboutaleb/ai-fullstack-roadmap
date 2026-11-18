"""Build entrypoint and interview renderer facade for the static roadmap site."""
from roadmap.site_builder import build_site as build, render_interview as interview

__all__ = ['build', 'interview']

if __name__ == '__main__':
    build()
