"""
Tensor Chunk Cache - Lightweight Redis Alternative for Resource-Constrained Environments

A memory-efficient caching system designed for QMNF AI development stack that:
- Performs automatic tensor chunking to avoid memory bottlenecks
- Uses memory-mapped files for disk-backed storage
- Implements LRU eviction with configurable memory limits
- Provides Redis-compatible API for AI framework integration
- Follows QMNF integer-only architecture principles

Author: QMNF System
License: Proprietary
"""

import fnmatch
import mmap
import pickle
import struct
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Optional, Dict, List
import hashlib


class TensorChunkCache:
    """
    Lightweight caching system with automatic tensor chunking.

    Designed to replace Redis in resource-constrained environments by:
    1. Chunking large tensors into manageable pieces
    2. Using memory-mapped files for efficient disk-backed storage
    3. Implementing LRU eviction to stay within memory limits
    4. Providing Redis-compatible API for AI frameworks

    Memory Layout (all integers):
    - Header: magic number (8 bytes) + version (4 bytes) + num_entries (8 bytes)
    - Entry: key_hash (8 bytes) + offset (8 bytes) + size (8 bytes) + timestamp (8 bytes)
    - Data: chunked payload with chunk headers
    """

    # Integer constants (no floats)
    MAGIC_NUMBER = 0x514D4E46_54434348  # "QMNFTCCH" in hex
    VERSION = 1
    HEADER_SIZE = 20  # bytes (magic + version + num_entries)
    ENTRY_SIZE = 32   # bytes (key_hash + offset + size + timestamp)
    DEFAULT_CHUNK_SIZE = 1048576  # 1 MB chunks (integer)
    DEFAULT_MAX_MEMORY = 104857600  # 100 MB (integer)

    def __init__(
        self,
        cache_dir: str = "/tmp/qmnf_cache",
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        max_memory: int = DEFAULT_MAX_MEMORY,
        max_entries: int = 10000
    ):
        """
        Initialize tensor chunk cache.

        Args:
            cache_dir: Directory for cache files
            chunk_size: Size of each tensor chunk in bytes (integer)
            max_memory: Maximum memory usage in bytes (integer)
            max_entries: Maximum number of cache entries (integer)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # All configuration values are integers
        self.chunk_size = chunk_size
        self.max_memory = max_memory
        self.max_entries = max_entries

        # In-memory LRU cache (metadata only)
        self.lru_cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # Memory-mapped file for persistent storage
        self.storage_path = self.cache_dir / "cache.mmap"
        self.index_path = self.cache_dir / "index.bin"
        self.key_map_path = self.cache_dir / "keys.pkl"

        # Current memory usage (integer bytes)
        self.current_memory = 0

        # Next available offset for writing (integer bytes)
        self.next_offset = 0

        # Map hashed keys to original keys for Redis compatibility
        self.key_map: Dict[str, str] = {}

        # Track metadata persistence frequency
        self._metadata_dirty_operations = 0
        self._metadata_save_interval = 100

        # Initialize or load existing cache
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize memory-mapped storage and load index."""
        # Create empty storage if doesn't exist
        if not self.storage_path.exists():
            # Pre-allocate storage file (integer size)
            initial_size = self.max_memory
            with open(self.storage_path, 'wb') as f:
                f.write(b'\x00' * initial_size)

        # Open memory-mapped file
        self.storage_file = open(self.storage_path, 'r+b')
        self.storage_mmap = mmap.mmap(
            self.storage_file.fileno(),
            0,
            access=mmap.ACCESS_WRITE
        )

        # Load index if exists
        if self.index_path.exists():
            self._load_index()
        else:
            self._create_index()

        # Load key mapping for Redis compatibility
        self._load_key_map()

    def _create_index(self):
        """Create new index file with header."""
        with open(self.index_path, 'wb') as f:
            # Write header: magic (8) + version (4) + num_entries (8)
            f.write(struct.pack('QIQ', self.MAGIC_NUMBER, self.VERSION, 0))

    def _load_key_map(self):
        """Load mapping of hashed keys to original keys."""
        self.key_map = {}

        if self.key_map_path.exists():
            try:
                with open(self.key_map_path, 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        for hex_key, original_key in data.items():
                            if isinstance(hex_key, str) and isinstance(original_key, str):
                                self.key_map[hex_key] = original_key
            except (pickle.UnpicklingError, EOFError, OSError, AttributeError):
                # Corrupted or incompatible map - start fresh
                self.key_map = {}

        # Ensure every cache entry has an associated original key
        for hex_key, entry in self.lru_cache.items():
            original_key = self.key_map.get(hex_key, hex_key)
            entry.original_key = original_key
            if hex_key not in self.key_map:
                self.key_map[hex_key] = original_key

    def _save_key_map(self):
        """Persist key mapping to disk."""
        try:
            with open(self.key_map_path, 'wb') as f:
                pickle.dump(self.key_map, f)
        except (OSError, pickle.PickleError):
            # Graceful failure - continue operating in-memory
            pass

    def _mark_metadata_dirty(self):
        """Track metadata updates and periodically persist to disk."""
        self._metadata_dirty_operations += 1
        if self._metadata_dirty_operations >= self._metadata_save_interval:
            self._persist_metadata()

    def _persist_metadata(self, force: bool = False):
        """Persist index and key mapping when dirty or forced."""
        if not force and self._metadata_dirty_operations == 0:
            return

        try:
            self._save_index()
        except (IOError, OSError):
            pass

        self._save_key_map()
        self._metadata_dirty_operations = 0

    def _load_index(self):
        """Load index from disk and populate LRU cache."""
        with open(self.index_path, 'rb') as f:
            # Read header
            magic, version, num_entries = struct.unpack('QIQ', f.read(self.HEADER_SIZE))

            if magic != self.MAGIC_NUMBER:
                raise ValueError("Invalid cache index file")

            if version != self.VERSION:
                raise ValueError(f"Unsupported cache version: {version}")

            # Read entries
            for _ in range(num_entries):
                entry_data = f.read(self.ENTRY_SIZE)
                if len(entry_data) < self.ENTRY_SIZE:
                    break

                key_hash, offset, size, timestamp = struct.unpack('QQQQ', entry_data)

                # Reconstruct cache entry
                entry = CacheEntry(
                    key_hash=key_hash,
                    offset=offset,
                    size=size,
                    timestamp=timestamp,
                    chunks=self._calculate_num_chunks(size)
                )

                # Add to LRU cache (use hex hash as key)
                key = f"{key_hash:016x}"
                self.lru_cache[key] = entry
                self.current_memory += size

            # Update next_offset to max offset seen
            max_offset = max(
                (entry.offset + entry.size for entry in self.lru_cache.values()),
                default=0
            )
            self.next_offset = max_offset

    def _save_index(self):
        """Save index to disk."""
        with open(self.index_path, 'wb') as f:
            # Write header
            f.write(struct.pack('QIQ', self.MAGIC_NUMBER, self.VERSION, len(self.lru_cache)))

            # Write entries
            for entry in self.lru_cache.values():
                f.write(struct.pack(
                    'QQQQ',
                    entry.key_hash,
                    entry.offset,
                    entry.size,
                    entry.timestamp
                ))

    def _calculate_num_chunks(self, size: int) -> int:
        """Calculate number of chunks needed for given size (integer division)."""
        return (size + self.chunk_size - 1) // self.chunk_size

    def _hash_key(self, key: str) -> int:
        """Generate 64-bit integer hash from key."""
        hash_bytes = hashlib.sha256(key.encode('utf-8')).digest()
        return struct.unpack('Q', hash_bytes[:8])[0]

    def _evict_lru(self, required_space: int):
        """Evict least recently used entries to free required space."""
        while self.current_memory + required_space > self.max_memory and self.lru_cache:
            # Remove oldest entry (FIFO order from OrderedDict)
            key, entry = self.lru_cache.popitem(last=False)
            self.current_memory -= entry.size
            self.key_map.pop(key, None)
            self._mark_metadata_dirty()

    def _allocate_space(self, size: int) -> int:
        """Allocate space in storage and return offset (integer arithmetic)."""
        # If not enough space, flush cache and start over
        if self.next_offset + size > self.max_memory:
            # Simple strategy for resource-constrained environments:
            # Flush entire cache and start over
            self.lru_cache.clear()
            self.current_memory = 0
            self.next_offset = 0
            self.key_map.clear()
            self._mark_metadata_dirty()

        # Return current offset and increment for next allocation
        offset = self.next_offset
        self.next_offset += size

        return offset

    def _write_chunks(self, data: bytes, offset: int) -> int:
        """
        Write data in chunks to memory-mapped storage.

        Fails gracefully if storage is full by returning 0.
        """
        try:
            data_offset = 0  # Track position in original data
            storage_offset = offset  # Track position in storage
            chunk_idx = 0

            while data_offset < len(data):
                # Calculate chunk bounds (integer arithmetic)
                chunk_end = min(data_offset + self.chunk_size, len(data))
                chunk_data = data[data_offset:chunk_end]

                # Check if we have space
                if storage_offset + 8 + len(chunk_data) > len(self.storage_mmap):
                    # Storage full - fail gracefully
                    return 0

                # Write chunk header: chunk_idx (4) + chunk_size (4) + data
                header = struct.pack('II', chunk_idx, len(chunk_data))

                self.storage_mmap[storage_offset:storage_offset + 8] = header
                self.storage_mmap[storage_offset + 8:storage_offset + 8 + len(chunk_data)] = chunk_data

                data_offset += len(chunk_data)
                storage_offset += 8 + len(chunk_data)
                chunk_idx += 1

            return storage_offset - offset  # Total bytes written to storage

        except (IndexError, ValueError):
            # Graceful failure: storage full or corruption
            return 0

    def _read_chunks(self, offset: int, size: int) -> Optional[bytes]:
        """
        Read chunked data from memory-mapped storage.

        Returns None on failure (graceful degradation).
        """
        try:
            chunks = []
            bytes_read = 0

            while bytes_read < size:
                # Check bounds
                read_offset = offset + bytes_read
                if read_offset + 8 > len(self.storage_mmap):
                    # Read beyond storage bounds - return None
                    return None

                # Read chunk header
                chunk_idx, chunk_size = struct.unpack('II', self.storage_mmap[read_offset:read_offset + 8])

                # Validate chunk size
                if chunk_size > self.chunk_size or chunk_size == 0:
                    # Invalid chunk size - corruption detected
                    return None

                # Check if chunk data is within bounds
                if read_offset + 8 + chunk_size > len(self.storage_mmap):
                    return None

                # Read chunk data
                chunk_data = self.storage_mmap[read_offset + 8:read_offset + 8 + chunk_size]
                chunks.append(bytes(chunk_data))

                bytes_read += 8 + chunk_size

            return b''.join(chunks)

        except (struct.error, IndexError, ValueError):
            # Graceful failure: corruption or invalid data
            return None

    # Redis-compatible API

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set key to value (Redis-compatible).

        Args:
            key: Cache key
            value: Value to cache (will be pickled)
            ex: Expiration time in seconds (integer, optional)

        Returns:
            True if successful
        """
        # Serialize value
        data = pickle.dumps(value)
        data_size = len(data)

        # Calculate actual storage size (data + headers)
        num_chunks = self._calculate_num_chunks(data_size)
        storage_size = data_size + (num_chunks * 8)  # 8 bytes per chunk header

        # Generate key hash (integer)
        key_hash = self._hash_key(key)
        key_hex = f"{key_hash:016x}"

        # Check if key already exists
        if key_hex in self.lru_cache:
            old_entry = self.lru_cache[key_hex]
            self.current_memory -= old_entry.size

        # Allocate space for data + headers
        offset = self._allocate_space(storage_size)

        # Write chunks
        actual_size = self._write_chunks(data, offset)

        # Graceful failure: check if write succeeded
        if actual_size == 0:
            # Write failed (storage full), return False
            return False

        # Create cache entry (all integer fields)
        timestamp = int(time.time())
        entry = CacheEntry(
            key_hash=key_hash,
            offset=offset,
            size=actual_size,
            timestamp=timestamp,
            chunks=num_chunks,
            expiration=timestamp + ex if ex is not None else None,
            original_key=key
        )

        # Update LRU cache
        self.lru_cache[key_hex] = entry
        self.lru_cache.move_to_end(key_hex)
        self.current_memory += actual_size
        self.key_map[key_hex] = key
        self._mark_metadata_dirty()

        # Save metadata periodically
        if len(self.lru_cache) % self._metadata_save_interval == 0:
            self._persist_metadata()

        return True

    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key (Redis-compatible).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        key_hash = self._hash_key(key)
        key_hex = f"{key_hash:016x}"

        if key_hex not in self.lru_cache:
            return None

        entry = self.lru_cache[key_hex]

        # Check expiration (integer comparison)
        if entry.expiration is not None:
            current_time = int(time.time())
            if current_time >= entry.expiration:
                self.delete(key)
                return None

        # Update LRU
        self.lru_cache.move_to_end(key_hex)

        # Read chunks
        data = self._read_chunks(entry.offset, entry.size)

        # Graceful failure: check if read succeeded
        if data is None:
            # Read failed (corruption), remove entry and return None
            self.delete(key)
            return None

        # Deserialize
        try:
            return pickle.loads(data)
        except (pickle.UnpicklingError, EOFError):
            # Graceful failure: corrupted data, remove entry
            self.delete(key)
            return None

    def delete(self, key: str) -> bool:
        """
        Delete key (Redis-compatible).

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        key_hash = self._hash_key(key)
        key_hex = f"{key_hash:016x}"

        if key_hex not in self.lru_cache:
            return False

        entry = self.lru_cache.pop(key_hex)
        self.current_memory -= entry.size
        self.key_map.pop(key_hex, None)
        self._mark_metadata_dirty()

        return True

    def exists(self, key: str) -> bool:
        """Check if key exists (Redis-compatible)."""
        key_hash = self._hash_key(key)
        key_hex = f"{key_hash:016x}"
        return key_hex in self.lru_cache

    def keys(self, pattern: str = "*") -> List[str]:
        """
        Get all keys matching pattern (Redis-compatible).

        Returns the original key strings to mirror Redis semantics.
        """
        all_keys = list(self.key_map.values())
        if pattern == "*":
            return all_keys

        matched_keys: List[str] = []
        for original_key in all_keys:
            if fnmatch.fnmatch(original_key, pattern):
                matched_keys.append(original_key)

        return matched_keys

    def flushdb(self) -> bool:
        """Clear all cache entries (Redis-compatible)."""
        self.lru_cache.clear()
        self.current_memory = 0
        self.key_map.clear()
        self._create_index()
        # Remove persisted key map if present
        try:
            if self.key_map_path.exists():
                self.key_map_path.unlink()
        except OSError:
            pass
        self._persist_metadata(force=True)
        return True

    def info(self) -> Dict[str, int]:
        """
        Get cache statistics (Redis-compatible).

        Returns dictionary with integer values only.
        """
        return {
            'used_memory': self.current_memory,
            'max_memory': self.max_memory,
            'num_entries': len(self.lru_cache),
            'max_entries': self.max_entries,
            'chunk_size': self.chunk_size,
            'version': self.VERSION,
        }

    def close(self):
        """Close cache and save index."""
        self._persist_metadata(force=True)
        if self.storage_mmap:
            self.storage_mmap.close()
        if self.storage_file:
            self.storage_file.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class CacheEntry:
    """
    Cache entry metadata (all integer fields).

    Attributes:
        key_hash: 64-bit integer hash of key
        offset: Byte offset in storage file (integer)
        size: Total size in bytes (integer)
        timestamp: Unix timestamp (integer seconds)
        chunks: Number of chunks (integer)
        expiration: Expiration timestamp (integer seconds, optional)
    """

    def __init__(
        self,
        key_hash: int,
        offset: int,
        size: int,
        timestamp: int,
        chunks: int,
        expiration: Optional[int] = None,
        original_key: Optional[str] = None
    ):
        self.key_hash = key_hash
        self.offset = offset
        self.size = size
        self.timestamp = timestamp
        self.chunks = chunks
        self.expiration = expiration
        self.original_key = original_key


# Drop-in Redis replacement for AI frameworks
class RedisCompatLayer:
    """
    Redis-compatible wrapper for TensorChunkCache.

    Provides exact Redis API for seamless integration with
    LangChain, CrewAI, AutoGen, and other AI frameworks.
    """

    def __init__(self, **kwargs):
        """Initialize with Redis-compatible arguments."""
        # Map Redis args to TensorChunkCache args
        cache_dir = kwargs.get('db', '/tmp/qmnf_cache')
        max_memory = kwargs.get('max_memory', TensorChunkCache.DEFAULT_MAX_MEMORY)

        self.cache = TensorChunkCache(
            cache_dir=f"/tmp/qmnf_cache_{cache_dir}",
            max_memory=max_memory
        )

    # Delegate all Redis methods to TensorChunkCache
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        return self.cache.set(key, value, ex)

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if self.cache.delete(key):
                count += 1
        return count

    def exists(self, *keys: str) -> int:
        return sum(1 for key in keys if self.cache.exists(key))

    def keys(self, pattern: str = "*") -> List[str]:
        return self.cache.keys(pattern)

    def flushdb(self) -> bool:
        return self.cache.flushdb()

    def info(self, section: Optional[str] = None) -> Dict[str, Any]:
        return self.cache.info()

    def close(self):
        self.cache.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Usage example for AI frameworks
if __name__ == "__main__":
    # Example 1: Direct usage
    with TensorChunkCache(max_memory=10_485_760) as cache:  # 10 MB limit
        # Cache large tensor (will be chunked automatically)
        large_data = b"x" * 5_000_000  # 5 MB
        cache.set("large_tensor", large_data)

        # Retrieve
        retrieved = cache.get("large_tensor")
        assert retrieved == large_data

        # Check stats
        stats = cache.info()
        print(f"Memory used: {stats['used_memory']} / {stats['max_memory']} bytes")
        print(f"Entries: {stats['num_entries']}")

    # Example 2: Redis-compatible usage for AI frameworks
    # Replace: redis.Redis() with RedisCompatLayer()
    cache = RedisCompatLayer(db=0)
    cache.set("llm_response", {"role": "assistant", "content": "Hello"}, ex=3600)
    response = cache.get("llm_response")
    print(f"Cached LLM response: {response}")
    cache.close()
