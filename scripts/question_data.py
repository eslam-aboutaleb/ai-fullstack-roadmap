"""Compatibility facade delegating question/search shard generation to roadmap.practice."""
from roadmap.practice import SHARD_SIZE, build_question_shards as build, build_search_shards as search_shards

__all__ = ['SHARD_SIZE', 'build', 'search_shards']
