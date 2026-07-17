"""wood-quality-assessment scripts package.

Production-grade automation and utility scripts:

- ``hooks_system``  — lifecycle hooks, state management, and event emission.
- ``skill_loader``  — dynamic skill discovery, resolution, and LRU caching.
- ``validator``     — JSON-schema validation and quality-gate checking.
- ``setup``         — project initialization, validation, and seeding routine.

All modules are runnable directly, e.g.::

    python -m scripts.setup init
    python -m scripts.setup validate
    python -m scripts.skill_loader
"""

__version__ = "1.0.1"
__all__ = ["hooks_system", "skill_loader", "validator", "setup"]
