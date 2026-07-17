"""
Wood Quality Assessment - Skill Loader
Implements dynamic skill discovery, loading, and resolution with caching.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import (
    Any,
)

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("wqa.skill_loader")


class SkillType(Enum):
    """Types of skills in the registry."""

    MAIN_HARNESS = "main_harness"
    SUB_SKILL = "sub_skill"
    UTILITY = "utility"


@dataclass
class SkillMetadata:
    """Metadata for a registered skill."""

    name: str
    description: str
    file_path: Path
    skill_type: SkillType
    version: str = "1.0.0"
    author: str = ""
    dependencies: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    frontmatter: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "file_path": str(self.file_path),
            "skill_type": self.skill_type.value,
            "version": self.version,
            "author": self.author,
            "dependencies": self.dependencies,
            "aliases": self.aliases,
            "tags": self.tags,
            "frontmatter": self.frontmatter,
        }


@dataclass
class CacheEntry:
    """Cache entry for loaded skills."""

    content: str
    metadata: SkillMetadata
    loaded_at: datetime
    access_count: int = 0
    last_accessed: datetime | None = None

    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() - self.loaded_at > timedelta(seconds=ttl_seconds)

    def touch(self) -> None:
        """Update access time and count."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class SkillLoader:
    """Dynamic skill discovery and loading with caching."""

    def __init__(
        self, scan_paths: list[Path] | None = None, cache_ttl: int = 3600, cache_size: int = 100
    ):
        self.scan_paths = scan_paths or [Path("skills/")]
        self.cache_ttl = cache_ttl
        self.cache_size = cache_size
        self._cache: dict[str, CacheEntry] = {}
        self._registry: dict[str, SkillMetadata] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from settings.yaml."""
        config_path = Path("config/settings.yaml")
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    if "skill_registry" in config:
                        sr_config = config["skill_registry"]
                        if sr_config.get("enabled", True):
                            if "scan_paths" in sr_config:
                                self.scan_paths = [Path(p) for p in sr_config["scan_paths"]]
                            self.cache_ttl = sr_config.get("cache_ttl", self.cache_ttl)
                        logger.info(f"Loaded skill registry config: {len(self.scan_paths)} paths")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

    def discover_skills(self, force_reload: bool = False) -> dict[str, SkillMetadata]:
        """Discover and register all skills in scan paths."""
        if self._registry and not force_reload:
            return self._registry

        self._registry = {}

        for scan_path in self.scan_paths:
            if not scan_path.exists():
                logger.warning(f"Scan path does not exist: {scan_path}")
                continue

            for skill_file in scan_path.rglob("*.md"):
                metadata = self._parse_skill_file(skill_file)
                if metadata:
                    self._register_skill(metadata)

        logger.info(f"Discovered {len(self._registry)} skills")
        return self._registry

    def _parse_skill_file(self, file_path: Path) -> SkillMetadata | None:
        """Parse a skill file and extract metadata."""
        try:
            content = file_path.read_text(encoding="utf-8")
            frontmatter = self._extract_frontmatter(content)

            if not frontmatter or "name" not in frontmatter:
                logger.warning(f"No valid frontmatter in {file_path}")
                return None

            # Determine skill type
            skill_type = self._determine_skill_type(file_path, frontmatter)

            return SkillMetadata(
                name=frontmatter["name"],
                description=frontmatter.get("description", ""),
                file_path=file_path,
                skill_type=skill_type,
                version=frontmatter.get("version", "1.0.0"),
                author=frontmatter.get("author", ""),
                dependencies=frontmatter.get("dependencies", []),
                aliases=frontmatter.get("aliases", []),
                tags=frontmatter.get("tags", []),
                frontmatter=frontmatter,
            )

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None

    def _extract_frontmatter(self, content: str) -> dict[str, Any] | None:
        """Extract YAML frontmatter from content."""
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if not match:
            return None

        try:
            return yaml.safe_load(match.group(1))
        except Exception as e:
            logger.warning(f"Failed to parse frontmatter: {e}")
            return None

    def _determine_skill_type(self, file_path: Path, frontmatter: dict[str, Any]) -> SkillType:
        """Determine skill type from file path and frontmatter."""
        # Check frontmatter first
        if "skill_type" in frontmatter:
            type_str = frontmatter["skill_type"]
            try:
                return SkillType(type_str)
            except ValueError:
                pass

        # Determine from file path
        if file_path.name == "main.md":
            return SkillType.MAIN_HARNESS
        elif file_path.parent.name == "sub-skills" or file_path.name.startswith("sub-"):
            return SkillType.SUB_SKILL
        else:
            return SkillType.UTILITY

    def _register_skill(self, metadata: SkillMetadata) -> None:
        """Register a skill in the registry."""
        self._registry[metadata.name] = metadata

        # Register aliases
        for alias in metadata.aliases:
            if alias not in self._registry:
                self._registry[alias] = metadata

        logger.debug(f"Registered skill: {metadata.name}")

    def resolve(self, skill_name: str, fuzzy: bool = True) -> SkillMetadata | None:
        """Resolve a skill name to metadata."""
        # Direct lookup
        if skill_name in self._registry:
            return self._registry[skill_name]

        # Alias lookup
        for metadata in self._registry.values():
            if skill_name in metadata.aliases:
                return metadata

        # Fuzzy matching
        if fuzzy:
            return self._fuzzy_match(skill_name)

        return None

    def _fuzzy_match(self, skill_name: str, max_distance: int = 2) -> SkillMetadata | None:
        """Find closest matching skill name using Levenshtein distance."""

        def levenshtein(s1: str, s2: str) -> int:
            """Calculate Levenshtein distance between two strings."""
            if len(s1) < len(s2):
                return levenshtein(s2, s1)

            if len(s2) == 0:
                return len(s1)

            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row

            return previous_row[-1]

        best_match = None
        best_distance = max_distance + 1

        for name, metadata in self._registry.items():
            distance = levenshtein(skill_name, name)
            if distance < best_distance:
                best_distance = distance
                best_match = metadata

        return best_match

    def load(self, skill_name: str) -> str | None:
        """Load skill content from cache or disk."""
        metadata = self.resolve(skill_name)
        if not metadata:
            logger.error(f"Skill not found: {skill_name}")
            return None

        # Check cache
        cache_key = metadata.name
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired(self.cache_ttl):
                entry.touch()
                logger.debug(f"Cache hit for {skill_name}")
                return entry.content

        # Load from disk
        try:
            content = metadata.file_path.read_text(encoding="utf-8")

            # Add to cache
            self._add_to_cache(cache_key, content, metadata)

            logger.info(f"Loaded skill: {skill_name} from {metadata.file_path}")
            return content

        except Exception as e:
            logger.error(f"Failed to load {skill_name}: {e}")
            return None

    def _add_to_cache(self, key: str, content: str, metadata: SkillMetadata) -> None:
        """Add skill content to cache with LRU eviction."""
        # Evict oldest if at capacity
        if len(self._cache) >= self.cache_size:
            oldest_key = min(
                self._cache.keys(), key=lambda k: self._cache[k].last_accessed or datetime.min
            )
            del self._cache[oldest_key]
            logger.debug(f"Evicted from cache: {oldest_key}")

        self._cache[key] = CacheEntry(content=content, metadata=metadata, loaded_at=datetime.now())

    def invalidate(self, skill_name: str) -> None:
        """Invalidate cached skill."""
        if skill_name in self._cache:
            del self._cache[skill_name]
            logger.debug(f"Invalidated cache for {skill_name}")

    def invalidate_all(self) -> None:
        """Invalidate all cached skills."""
        self._cache.clear()
        logger.info("Invalidated all cache")

    def get_registry(self) -> dict[str, SkillMetadata]:
        """Get current skill registry."""
        return self._registry.copy()

    def get_skills_by_type(self, skill_type: SkillType) -> list[SkillMetadata]:
        """Get all skills of a specific type."""
        return [
            metadata for metadata in self._registry.values() if metadata.skill_type == skill_type
        ]

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        if not self._cache:
            return {
                "size": 0,
                "capacity": self.cache_size,
                "entries": 0,
                "total_accesses": 0,
                "hit_entries": 0,
            }

        total_accesses = sum(entry.access_count for entry in self._cache.values())
        hit_entries = [entry for entry in self._cache.values() if entry.access_count > 0]

        return {
            "size": len(self._cache),
            "capacity": self.cache_size,
            "entries": [
                {
                    "key": key,
                    "loaded_at": entry.loaded_at.isoformat(),
                    "access_count": entry.access_count,
                    "last_accessed": entry.last_accessed.isoformat()
                    if entry.last_accessed
                    else None,
                }
                for key, entry in sorted(
                    self._cache.items(), key=lambda x: x[1].access_count, reverse=True
                )[:10]  # Top 10
            ],
            "total_accesses": total_accesses,
            "hit_entries": len(hit_entries),
        }

    def export_registry(self, output_path: Path) -> None:
        """Export skill registry to JSON file."""
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_skills": len(self._registry),
            "skills": {name: metadata.to_dict() for name, metadata in self._registry.items()},
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        logger.info(f"Exported registry to {output_path}")


# Singleton instance
_loader_instance: SkillLoader | None = None


def get_loader() -> SkillLoader:
    """Get global skill loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = SkillLoader()
        _loader_instance.discover_skills()
    return _loader_instance


@lru_cache(maxsize=100)
def load_skill(skill_name: str) -> str | None:
    """Load skill content with LRU caching (function-level)."""
    loader = get_loader()
    return loader.load(skill_name)


def resolve_skill(skill_name: str, fuzzy: bool = True) -> SkillMetadata | None:
    """Resolve skill name to metadata."""
    loader = get_loader()
    return loader.resolve(skill_name, fuzzy=fuzzy)


def list_skills(skill_type: SkillType | None = None) -> list[SkillMetadata]:
    """List all registered skills, optionally filtered by type."""
    loader = get_loader()
    if skill_type:
        return loader.get_skills_by_type(skill_type)
    return list(loader.get_registry().values())


def reload_registry() -> dict[str, SkillMetadata]:
    """Force reload skill registry."""
    loader = get_loader()
    loader.invalidate_all()
    return loader.discover_skills(force_reload=True)


# CLI interface
if __name__ == "__main__":
    import sys

    loader = SkillLoader()
    loader.discover_skills()

    print("Wood Quality Assessment - Skill Loader")
    print("=" * 60)

    # List all skills
    print("\nRegistered Skills:")
    for name, metadata in sorted(loader.get_registry().items()):
        print(f"  {name:30s} - {metadata.skill_type.value}")

    # Cache stats
    print("\nCache Statistics:")
    stats = loader.get_cache_stats()
    print(f"  Size: {stats['size']}/{stats['capacity']}")
    print(f"  Total accesses: {stats['total_accesses']}")

    # Test resolution
    if len(sys.argv) > 1:
        skill_name = sys.argv[1]
        print(f"\nResolving: {skill_name}")
        metadata = loader.resolve(skill_name)
        if metadata:
            print(f"  Found: {metadata.name}")
            print(f"  Type: {metadata.skill_type.value}")
            print(f"  File: {metadata.file_path}")
        else:
            print("  Not found")
