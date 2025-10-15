package com.deepstudyai.coach.services

import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.Logger
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.locks.ReentrantReadWriteLock
import kotlin.concurrent.read
import kotlin.concurrent.write

/**
 * Application-level cache service for Coach analysis results.
 *
 * Provides fast access to previously computed analysis results,
 * reducing API calls and improving performance.
 */
@Service(Service.Level.APP)
class CoachCacheService {

    private val log = Logger.getInstance(CoachCacheService::class.java)
    private val cache = ConcurrentHashMap<String, CacheEntry>()
    private val lock = ReentrantReadWriteLock()

    companion object {
        fun getInstance(): CoachCacheService = service()
    }

    /**
     * Gets a value from the cache.
     */
    fun get(key: String): Any? = lock.read {
        val settings = CoachSettingsService.getInstance().state
        if (!settings.enableCaching) {
            return null
        }

        val entry = cache[key] ?: return null

        // Check if expired
        val expirationMs = settings.cacheExpirationMinutes * 60 * 1000L
        if (System.currentTimeMillis() - entry.timestamp > expirationMs) {
            cache.remove(key)
            return null
        }

        entry.accessCount++
        entry.lastAccessed = System.currentTimeMillis()
        return entry.value
    }

    /**
     * Puts a value in the cache.
     */
    fun put(key: String, value: Any) = lock.write {
        val settings = CoachSettingsService.getInstance().state
        if (!settings.enableCaching) {
            return
        }

        // Check cache size limit
        if (cache.size >= settings.maxCacheSize) {
            evictLeastRecentlyUsed()
        }

        cache[key] = CacheEntry(
            value = value,
            timestamp = System.currentTimeMillis(),
            lastAccessed = System.currentTimeMillis(),
            accessCount = 0
        )
    }

    /**
     * Removes a value from the cache.
     */
    fun remove(key: String) = lock.write {
        cache.remove(key)
    }

    /**
     * Clears all entries from the cache.
     */
    fun clear() = lock.write {
        cache.clear()
        log.info("Cache cleared")
    }

    /**
     * Removes expired entries from the cache.
     */
    fun cleanExpired() = lock.write {
        val settings = CoachSettingsService.getInstance().state
        val expirationMs = settings.cacheExpirationMinutes * 60 * 1000L
        val now = System.currentTimeMillis()

        val expiredKeys = cache.entries
            .filter { (_, entry) -> now - entry.timestamp > expirationMs }
            .map { it.key }

        expiredKeys.forEach { cache.remove(it) }

        if (expiredKeys.isNotEmpty()) {
            log.debug("Removed ${expiredKeys.size} expired cache entries")
        }
    }

    /**
     * Gets cache statistics.
     */
    fun getStatistics(): CacheStatistics = lock.read {
        val settings = CoachSettingsService.getInstance().state
        val expirationMs = settings.cacheExpirationMinutes * 60 * 1000L
        val now = System.currentTimeMillis()

        val validEntries = cache.values.count { now - it.timestamp <= expirationMs }
        val expiredEntries = cache.size - validEntries

        val totalAccesses = cache.values.sumOf { it.accessCount }
        val averageAccessCount = if (cache.isNotEmpty()) {
            totalAccesses.toDouble() / cache.size
        } else {
            0.0
        }

        CacheStatistics(
            totalEntries = cache.size,
            validEntries = validEntries,
            expiredEntries = expiredEntries,
            totalAccesses = totalAccesses,
            averageAccessCount = averageAccessCount,
            memorySizeEstimate = estimateMemorySize()
        )
    }

    /**
     * Checks if a key exists in the cache (and is not expired).
     */
    fun contains(key: String): Boolean = lock.read {
        val entry = cache[key] ?: return false

        val settings = CoachSettingsService.getInstance().state
        val expirationMs = settings.cacheExpirationMinutes * 60 * 1000L

        return System.currentTimeMillis() - entry.timestamp <= expirationMs
    }

    /**
     * Gets the size of the cache.
     */
    fun size(): Int = lock.read {
        cache.size
    }

    /**
     * Evicts the least recently used entry.
     */
    private fun evictLeastRecentlyUsed() {
        if (cache.isEmpty()) return

        val lruKey = cache.entries
            .minByOrNull { it.value.lastAccessed }
            ?.key

        lruKey?.let {
            cache.remove(it)
            log.debug("Evicted LRU cache entry: $it")
        }
    }

    /**
     * Evicts entries by access pattern (LRU with access count consideration).
     */
    private fun evictByAccessPattern() {
        if (cache.isEmpty()) return

        // Calculate score: lower is more likely to be evicted
        // Score = accessCount / (timeSinceLastAccess in hours)
        val now = System.currentTimeMillis()
        val evictKey = cache.entries
            .minByOrNull { (_, entry) ->
                val hoursSinceAccess = (now - entry.lastAccessed) / (1000.0 * 60 * 60)
                if (hoursSinceAccess < 0.01) {
                    Double.MAX_VALUE // Recently accessed, don't evict
                } else {
                    entry.accessCount / hoursSinceAccess
                }
            }?.key

        evictKey?.let {
            cache.remove(it)
            log.debug("Evicted cache entry by access pattern: $it")
        }
    }

    /**
     * Estimates memory usage of the cache in bytes.
     */
    private fun estimateMemorySize(): Long {
        // Rough estimation: 1KB per entry on average
        return cache.size * 1024L
    }

    /**
     * Invalidates cache entries matching a pattern.
     */
    fun invalidatePattern(pattern: Regex) = lock.write {
        val keysToRemove = cache.keys.filter { pattern.matches(it) }
        keysToRemove.forEach { cache.remove(it) }

        if (keysToRemove.isNotEmpty()) {
            log.debug("Invalidated ${keysToRemove.size} cache entries matching pattern")
        }
    }

    /**
     * Invalidates cache entries for a specific file.
     */
    fun invalidateFile(filePath: String) {
        val pattern = Regex("^${Regex.escape(filePath)}:.*")
        invalidatePattern(pattern)
    }

    /**
     * Warms up the cache with common queries.
     */
    fun warmUp(entries: Map<String, Any>) = lock.write {
        entries.forEach { (key, value) ->
            put(key, value)
        }
        log.info("Cache warmed up with ${entries.size} entries")
    }
}

/**
 * A cache entry with metadata.
 */
private data class CacheEntry(
    val value: Any,
    val timestamp: Long,
    var lastAccessed: Long,
    var accessCount: Int
)

/**
 * Statistics about the cache.
 */
data class CacheStatistics(
    val totalEntries: Int,
    val validEntries: Int,
    val expiredEntries: Int,
    val totalAccesses: Int,
    val averageAccessCount: Double,
    val memorySizeEstimate: Long
)
