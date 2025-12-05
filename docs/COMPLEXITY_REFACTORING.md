# Code Complexity Refactoring Backlog

This document tracks functions with cognitive complexity > 15 that need refactoring.

## Critical Priority (Complexity >= 40)

### 1. DevToContentAnalyzer._determine_content_type - Complexity: 45

**File:** `src/devto_mirror/ai_optimization/content_analyzer.py:545`
**Current Complexity:** 45
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Extract content type detection logic into separate helper methods
- Create a mapping/strategy pattern for content type detection
- Reduce nested conditionals using early returns

### 2. DevToSchemaGenerator.generate_article_schema - Complexity: 7 ✅

**File:** `src/devto_mirror/ai_optimization/schema_generator.py:252`
**Original Complexity:** 55
**Current Complexity:** 7
**Target Complexity:** ≤ 15

**Refactoring Completed:**

- Extracted author extraction into `_extract_author_info()`
- Extracted date handling into `_extract_dates()` with `_normalize_iso_date()` helper
- Extracted image handling into `_extract_images()`
- Extracted tags/keywords into `_extract_keywords()`
- Extracted engagement metrics into `_extract_engagement_metrics()`
- Extracted content metrics into `_extract_content_metrics()`
- Refactored main method as orchestrator calling helper methods

## High Priority (Complexity 20-39)

### 3. DevToMetadataEnhancer._determine_content_type - Complexity: 24

**File:** `src/devto_mirror/ai_optimization/metadata_enhancer.py:119`
**Current Complexity:** 24
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Similar to item #1, extract into helper methods
- Consider sharing logic with DevToContentAnalyzer._determine_content_type

### 4. DevToContentAnalyzer.extract_api_metrics - Complexity: 20

**File:** `src/devto_mirror/ai_optimization/content_analyzer.py:92`
**Current Complexity:** 20
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Extract API endpoint detection into separate method
- Extract metric calculation into helper functions
- Simplify conditional logic

### 5. DevToMetadataEnhancer._add_article_meta_tags - Complexity: 19

**File:** `src/devto_mirror/ai_optimization/metadata_enhancer.py:65`
**Current Complexity:** 19
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Extract Open Graph meta tags generation
- Extract Twitter Card meta tags generation
- Separate validation logic from generation logic

### 6. DevToAISitemapGenerator._determine_content_type - Complexity: 18

**File:** `src/devto_mirror/ai_optimization/sitemap_generator.py:312`
**Current Complexity:** 18
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Share implementation with other _determine_content_type methods
- Consider creating a base class or mixin for content type determination

### 7. _fetch_article_pages - Complexity: 18

**File:** `scripts/generate_site.py:78`
**Current Complexity:** 18
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Extract retry logic into separate function
- Extract response processing into helper method
- Simplify error handling with early returns

## Medium Priority (Complexity 16-19)

### 8. GitHubPagesCrawlerAnalyzer.analyze_robots_txt - Complexity: 17

**File:** `scripts/analyze_github_pages_crawlers.py:32`
**Current Complexity:** 17
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Extract robots.txt parsing into separate method
- Extract permission analysis into helper function
- Simplify user-agent handling logic

### 9. DevToMetadataEnhancer.add_source_attribution_metadata - Complexity: 17

**File:** `src/devto_mirror/ai_optimization/metadata_enhancer.py:251`
**Current Complexity:** 17
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Extract attribution link generation
- Extract metadata tag creation
- Separate validation from generation

### 10. DevToContentAnalyzer.extract_code_languages - Complexity: 16

**File:** `src/devto_mirror/ai_optimization/content_analyzer.py:212`
**Current Complexity:** 16
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Extract language detection patterns
- Extract confidence scoring logic
- Simplify nested loops

### 11. DevToSchemaGenerator (class) - Complexity: 17

**File:** `src/devto_mirror/ai_optimization/schema_generator.py:20`
**Current Complexity:** 17
**Target Complexity:** ≤ 15

**Refactoring Strategy:**

- Review class structure
- Consider splitting into multiple specialized classes
- Reduce method interdependencies

## Status Summary

- **Total Functions:** 11
- **Critical Priority (>= 40):** 2
- **High Priority (20-39):** 5
- **Medium Priority (16-19):** 4

## Refactoring Guidelines

1. **Maximum Cognitive Complexity:** 15 per function
2. **Extract Methods:** Break down complex functions into smaller, focused helpers
3. **Early Returns:** Use guard clauses to reduce nesting
4. **Strategy Pattern:** Use dictionaries/mappings instead of long if-else chains
5. **Single Responsibility:** Each function should do one thing well
6. **Code Reuse:** Look for duplicated logic across similar functions

## Progress Tracking

- [ ] DevToContentAnalyzer._determine_content_type (45)
- [x] DevToSchemaGenerator.generate_article_schema (55 → 7) ✅
- [ ] DevToMetadataEnhancer._determine_content_type (24)
- [ ] DevToContentAnalyzer.extract_api_metrics (20)
- [ ] DevToMetadataEnhancer._add_article_meta_tags (19)
- [ ] DevToAISitemapGenerator._determine_content_type (18)
- [ ] _fetch_article_pages (18)
- [ ] GitHubPagesCrawlerAnalyzer.analyze_robots_txt (17)
- [ ] DevToMetadataEnhancer.add_source_attribution_metadata (17)
- [ ] DevToContentAnalyzer.extract_code_languages (16)
- [x] DevToSchemaGenerator class (17 → 7) ✅
