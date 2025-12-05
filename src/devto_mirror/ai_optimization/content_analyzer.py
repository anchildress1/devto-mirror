"""
Content Analysis Module for Dev.to Mirror

This module provides content analysis functionality for Dev.to posts,
including metrics extraction, language detection, and content type classification.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

# Configure logging for content analysis
logger = logging.getLogger(__name__)


class DevToContentAnalyzer:
    """
    Content analyzer for Dev.to posts.

    Extracts metrics, detects programming languages, and determines content types
    from Dev.to posts, prioritizing API data when available.
    """

    def __init__(self):
        """Initialize content analyzer with logging configuration."""
        self.logger = logging.getLogger(__name__ + ".ContentAnalyzer")

    def analyze_post_content(self, post: Any, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze post content and extract semantic information.

        Args:
            post: Post object containing content
            api_data: Original Dev.to API response data

        Returns:
            Dictionary containing content analysis results with data source flags
        """
        analysis_result = {
            "metrics": {},
            "content_type": "",
            "code_languages": [],
            "data_source_flags": {},
            "analysis_timestamp": "",
        }

        try:
            # Extract metrics (API-first approach)
            api_metrics = self.extract_api_metrics(api_data)
            fallback_metrics = {}

            # Calculate fallback metrics if needed
            content_html = getattr(post, "content_html", "")
            if content_html and (not api_metrics or len(api_metrics) == 0):
                self.logger.info("Using fallback content analysis - API data not available")
                fallback_metrics = self.calculate_fallback_metrics(content_html)
            elif not api_metrics:
                self.logger.info("Using fallback content analysis - API metrics empty")
                fallback_metrics = self.calculate_fallback_metrics(content_html)

            # Combine metrics with data source tracking
            analysis_result["metrics"] = {**fallback_metrics, **api_metrics}

            # Track data sources
            analysis_result["data_source_flags"] = {
                "reading_time_source": "api" if "reading_time_minutes" in api_metrics else "calculated",
                "word_count_source": "api" if "word_count" in api_metrics else "calculated",
                "reactions_source": "api" if "public_reactions_count" in api_metrics else "unavailable",
                "api_data_available": bool(api_data and len(api_data) > 0),
            }

            # Determine content type
            analysis_result["content_type"] = self._determine_content_type(post, api_data)

            # Extract programming languages from code blocks and tags
            analysis_result["code_languages"] = self.extract_code_languages(content_html, api_data)

            # Add timestamp
            analysis_result["analysis_timestamp"] = datetime.now(timezone.utc).isoformat()

            self.logger.debug(f"Content analysis completed for post: {getattr(post, 'slug', 'unknown')}")

        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            # Return minimal analysis result on error
            analysis_result["metrics"] = self.calculate_fallback_metrics(getattr(post, "content_html", ""))
            analysis_result["data_source_flags"] = {"error": str(e)}

        return analysis_result

    def extract_api_metrics(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metrics directly from Dev.to API data when available.

        Args:
            api_data: Original Dev.to API response

        Returns:
            Dictionary of metrics extracted from API (reading_time, reactions, etc.)
        """
        metrics = {}

        if not api_data or not isinstance(api_data, dict):
            self.logger.debug("No API data available for metric extraction")
            return metrics

        try:
            # Extract reading time (Dev.to provides this)
            reading_time = api_data.get("reading_time_minutes")
            if reading_time is not None and isinstance(reading_time, (int, float)) and reading_time > 0:
                metrics["reading_time_minutes"] = int(reading_time)
                self.logger.debug(f"Extracted reading time from API: {reading_time} minutes")

            # Extract reaction count
            reactions = api_data.get("public_reactions_count")
            if reactions is not None and isinstance(reactions, (int, float)) and reactions >= 0:
                metrics["public_reactions_count"] = int(reactions)
                self.logger.debug(f"Extracted reaction count from API: {reactions}")

            # Extract comment count
            comments = api_data.get("comments_count")
            if comments is not None and isinstance(comments, (int, float)) and comments >= 0:
                metrics["comments_count"] = int(comments)

            # Extract word count if available (some APIs provide this)
            word_count = api_data.get("word_count")
            if word_count is not None and isinstance(word_count, (int, float)) and word_count > 0:
                metrics["word_count"] = int(word_count)

            # Extract page views if available
            page_views = api_data.get("page_views_count")
            if page_views is not None and isinstance(page_views, (int, float)) and page_views >= 0:
                metrics["page_views_count"] = int(page_views)

            if metrics:
                self.logger.info(f"Successfully extracted {len(metrics)} metrics from API data")
            else:
                self.logger.debug("No usable metrics found in API data")

        except Exception as e:
            self.logger.warning(f"Error extracting API metrics: {e}")

        return metrics

    def calculate_fallback_metrics(self, content: str) -> Dict[str, Any]:
        """
        Calculate basic metrics when API data is unavailable.

        Args:
            content: HTML content string to analyze

        Returns:
            Dictionary of calculated metrics (word_count, estimated_reading_time)
        """
        metrics = {}

        if not content or not isinstance(content, str):
            self.logger.debug("No content available for fallback metric calculation")
            return metrics

        try:
            # Remove HTML tags to get plain text
            text_content = re.sub(r"<[^>]+>", "", content)

            # Remove extra whitespace
            text_content = " ".join(text_content.split())

            # Calculate word count
            if text_content:
                words = text_content.split()
                word_count = len(words)
                metrics["word_count"] = word_count

                # Estimate reading time (average 200 words per minute)
                if word_count > 0:
                    reading_time_minutes = max(1, round(word_count / 200))
                    metrics["reading_time_minutes"] = reading_time_minutes

                self.logger.debug(
                    f"Calculated fallback metrics: {word_count} words, {reading_time_minutes} min reading time"
                )

            # Calculate content length metrics
            metrics["content_length_chars"] = len(content)
            metrics["text_length_chars"] = len(text_content)

            # Count code blocks (basic estimation)
            code_blocks = re.findall(r"<pre[^>]*>.*?</pre>", content, re.DOTALL | re.IGNORECASE)
            code_blocks += re.findall(r"<code[^>]*>.*?</code>", content, re.DOTALL | re.IGNORECASE)
            metrics["code_blocks_count"] = len(code_blocks)

            # Count images
            images = re.findall(r"<img[^>]*>", content, re.IGNORECASE)
            metrics["images_count"] = len(images)

            # Count links
            links = re.findall(r"<a[^>]*href[^>]*>", content, re.IGNORECASE)
            metrics["links_count"] = len(links)

        except Exception as e:
            self.logger.warning(f"Error calculating fallback metrics: {e}")
            # Provide minimal fallback
            metrics = {
                "word_count": 0,
                "reading_time_minutes": 1,
                "content_length_chars": len(content) if content else 0,
            }

        return metrics

    def extract_code_languages(self, content: str, api_data: Dict[str, Any] = None) -> List[str]:
        """
        Identify programming languages from code blocks in content and Dev.to tags.

        Args:
            content: HTML content containing code blocks
            api_data: Optional Dev.to API data containing tag_list

        Returns:
            List of detected programming language identifiers
        """
        languages = set()

        if api_data:
            tag_languages = self._extract_languages_from_tags(api_data)
            languages.update(tag_languages)

        if not content or not isinstance(content, str):
            return sorted(list(languages))

        try:
            languages.update(self._extract_languages_from_attributes(content))
            languages.update(self._extract_languages_from_fenced_blocks(content))

            code_content = self._extract_code_block_content(content)
            if code_content:
                detected_langs = self._detect_languages_by_keywords(code_content)
                languages.update(detected_langs)

            result = self._normalize_and_sort_languages(languages)

            if result:
                self.logger.debug(f"Detected programming languages: {result}")

            return result

        except Exception as e:
            self.logger.warning(f"Error extracting code languages: {e}")
            return []

    def _extract_languages_from_attributes(self, content: str) -> set:
        """Extract programming languages from HTML class and data attributes."""
        languages = set()
        lang_class_patterns = [
            r'class=["\'][^"\']*(?:language|lang)-([a-zA-Z0-9+#-]+)',
            r'data-lang=["\']([a-zA-Z0-9+#-]+)["\']',
            r'data-language=["\']([a-zA-Z0-9+#-]+)["\']',
        ]

        for pattern in lang_class_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                lang = match.lower().strip()
                if lang and len(lang) <= 20:
                    languages.add(lang)

        return languages

    def _extract_languages_from_fenced_blocks(self, content: str) -> set:
        """Extract programming languages from fenced code blocks (```language)."""
        languages = set()
        fenced_blocks = re.findall(r"```([a-zA-Z0-9+#-]+)", content)
        for lang in fenced_blocks:
            lang = lang.lower().strip()
            if lang and len(lang) <= 20:
                languages.add(lang)

        return languages

    def _normalize_and_sort_languages(self, languages: set) -> List[str]:
        """Normalize language names and return sorted list."""
        normalized_languages = []
        for lang in languages:
            normalized = self._normalize_language_name(lang)
            if normalized:
                normalized_languages.append(normalized)

        return sorted(list(set(normalized_languages)))

    def _extract_code_block_content(self, content: str) -> str:
        """Extract text content from code blocks for language detection."""
        code_blocks = []

        # Extract content from <pre> and <code> tags
        pre_blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", content, re.DOTALL | re.IGNORECASE)
        code_blocks.extend(pre_blocks)

        code_tags = re.findall(r"<code[^>]*>(.*?)</code>", content, re.DOTALL | re.IGNORECASE)
        code_blocks.extend(code_tags)

        # Clean HTML tags from extracted content
        combined_code = " ".join(code_blocks)
        clean_code = re.sub(r"<[^>]+>", "", combined_code)

        return clean_code

    def _detect_languages_by_keywords(self, code_content: str) -> List[str]:
        """Detect programming languages based on common keywords and patterns."""
        if not code_content or len(code_content.strip()) < 10:
            return []

        detected = []
        code_lower = code_content.lower()

        # Language detection patterns (basic heuristics)
        language_patterns = {
            "python": ["def ", "import ", "from ", "print(", "__init__", "elif ", "self."],
            "javascript": ["function ", "var ", "let ", "const ", "console.log", "=>", "document."],
            "typescript": ["interface ", "type ", ": string", ": number", ": boolean"],
            "java": ["public class", "private ", "public static void main", "System.out"],
            "csharp": ["using System", "public class", "Console.WriteLine", "namespace "],
            "cpp": ["#include", "std::", "cout <<", "int main()", "using namespace"],
            "c": ["#include", "printf(", "int main()", "malloc(", "free("],
            "go": ["package ", "func ", "import (", "fmt.Print", "go "],
            "rust": ["fn ", "let mut", "println!", "use std::", "impl "],
            "php": ["<?php", "echo ", "$_GET", "$_POST", "function "],
            "ruby": ["def ", "end", "puts ", "require ", "class "],
            "swift": ["func ", "var ", "let ", "import Foundation", "print("],
            "kotlin": ["fun ", "val ", "var ", "println(", "class "],
            "scala": ["def ", "val ", "var ", "object ", "class "],
            "sql": ["SELECT ", "FROM ", "WHERE ", "INSERT INTO", "UPDATE ", "DELETE "],
            "html": ["<html", "<div", "<span", "<body", "<!DOCTYPE"],
            "css": ["{", "}", "margin:", "padding:", "color:", "background:"],
            "bash": ["#!/bin/bash", "echo ", "export ", "if [", "fi"],
            "yaml": ["---", "- name:", "version:", "dependencies:"],
            "json": ['{"', '"}', '":', "[{", "}]"],
            "xml": ["<?xml", "</", "/>"],
        }

        for language, patterns in language_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in code_lower)
            # If we find multiple patterns for a language, it's likely that language
            if matches >= 2:
                detected.append(language)
            elif matches == 1 and len(patterns) <= 3:  # For languages with fewer patterns
                detected.append(language)

        return detected

    def _normalize_language_name(self, lang: str) -> str:
        """Normalize language names to standard identifiers."""
        if not lang:
            return ""

        lang = lang.lower().strip()

        # Language name mappings
        language_mappings = {
            "js": "javascript",
            "ts": "typescript",
            "py": "python",
            "rb": "ruby",
            "cs": "csharp",
            "c++": "cpp",
            "c#": "csharp",
            "golang": "go",
            "yml": "yaml",
            "sh": "bash",
            "shell": "bash",
            "htm": "html",
        }

        # Apply mappings
        normalized = language_mappings.get(lang, lang)

        # Validate that it's a reasonable language name
        if len(normalized) > 20 or not normalized.replace("+", "").replace("#", "").replace("-", "").isalnum():
            return ""

        return normalized

    def _extract_languages_from_tags(self, api_data: Dict[str, Any]) -> List[str]:
        """
        Extract programming languages from Dev.to tag_list.

        Args:
            api_data: Dev.to API response data

        Returns:
            List of programming languages found in tags
        """
        languages = set()

        if not api_data or not isinstance(api_data, dict):
            return []

        # Get tags from API data
        tags = api_data.get("tag_list", [])
        if not tags and "tags" in api_data:
            tags = api_data.get("tags", [])

        if not isinstance(tags, list):
            return []

        # Common programming language tags used on Dev.to
        programming_language_tags = {
            "javascript",
            "js",
            "typescript",
            "ts",
            "python",
            "py",
            "java",
            "csharp",
            "c#",
            "cs",
            "cpp",
            "c++",
            "c",
            "go",
            "golang",
            "rust",
            "php",
            "ruby",
            "rb",
            "swift",
            "kotlin",
            "scala",
            "dart",
            "r",
            "matlab",
            "perl",
            "lua",
            "haskell",
            "clojure",
            "elixir",
            "erlang",
            "fsharp",
            "f#",
            "ocaml",
            "nim",
            "crystal",
            "zig",
            "v",
            "julia",
            "bash",
            "shell",
            "powershell",
            "sql",
            "html",
            "css",
            "scss",
            "sass",
            "less",
            "xml",
            "yaml",
            "yml",
            "json",
            "toml",
            "ini",
            "dockerfile",
            "makefile",
            "assembly",
            "asm",
            "vhdl",
            "verilog",
            "solidity",
            "move",
            "cairo",
        }

        # Framework/library tags that imply languages
        framework_to_language = {
            "react": "javascript",
            "vue": "javascript",
            "angular": "javascript",
            "svelte": "javascript",
            "nodejs": "javascript",
            "node": "javascript",
            "express": "javascript",
            "nextjs": "javascript",
            "nuxtjs": "javascript",
            "gatsby": "javascript",
            "electron": "javascript",
            "django": "python",
            "flask": "python",
            "fastapi": "python",
            "pandas": "python",
            "numpy": "python",
            "tensorflow": "python",
            "pytorch": "python",
            "scikit": "python",
            "spring": "java",
            "springboot": "java",
            "hibernate": "java",
            "maven": "java",
            "gradle": "java",
            "dotnet": "csharp",
            "aspnet": "csharp",
            "blazor": "csharp",
            "xamarin": "csharp",
            "rails": "ruby",
            "sinatra": "ruby",
            "jekyll": "ruby",
            "laravel": "php",
            "symfony": "php",
            "wordpress": "php",
            "drupal": "php",
            "gin": "go",
            "echo": "go",
            "fiber": "go",
            "beego": "go",
            "actix": "rust",
            "rocket": "rust",
            "warp": "rust",
            "tokio": "rust",
            "flutter": "dart",
            "android": "java",
            "ios": "swift",
            "swiftui": "swift",
            "bootstrap": "css",
            "tailwind": "css",
            "bulma": "css",
            "materialize": "css",
        }

        # Check each tag
        for tag in tags:
            if not isinstance(tag, str):
                continue

            tag_lower = tag.lower().strip()

            # Direct language match
            if tag_lower in programming_language_tags:
                normalized = self._normalize_language_name(tag_lower)
                if normalized:
                    languages.add(normalized)

            # Framework/library implies language
            elif tag_lower in framework_to_language:
                implied_lang = framework_to_language[tag_lower]
                normalized = self._normalize_language_name(implied_lang)
                if normalized:
                    languages.add(normalized)

        result = sorted(list(languages))
        if result:
            self.logger.debug(f"Extracted languages from tags: {result}")

        return result

    def _determine_content_type(self, post: Any, api_data: Dict[str, Any]) -> str:
        """
        Determine the content type of the post based on tags and content.

        Args:
            post: Post object to analyze
            api_data: Original Dev.to API response data

        Returns:
            String indicating content type (tutorial, article, discussion, etc.)
        """
        # Get tags from API data first, then post object
        tags = []
        if api_data and "tags" in api_data:
            tags = api_data.get("tags", [])
        elif api_data and "tag_list" in api_data:
            tags = api_data.get("tag_list", [])

        if not tags:
            tags = getattr(post, "tags", [])

        if not isinstance(tags, list):
            tags = []

        # Convert tags to lowercase for comparison
        tags_lower = [tag.lower() for tag in tags if isinstance(tag, str)]

        # Determine content type based on tags and title
        title = getattr(post, "title", "").lower()

        # Tutorial/Guide content - based on actual Dev.to tags
        if any(tag in tags_lower for tag in ["tutorial", "howto", "guide", "walkthrough", "stepbystep", "beginners"]):
            return "tutorial"
        elif any(word in title for word in ["how to", "tutorial", "guide", "walkthrough", "step by step"]):
            return "tutorial"

        # Discussion/Community content - based on actual Dev.to tags
        elif any(
            tag in tags_lower for tag in ["discuss", "discussion", "watercooler", "community", "opinion", "thoughts"]
        ):
            return "discussion"
        elif any(word in title for word in ["thoughts on", "opinion", "discussion", "what do you think"]):
            return "discussion"

        # Career/Professional content - based on actual Dev.to tags
        elif any(tag in tags_lower for tag in ["career", "job", "interview", "workplace", "professional"]):
            return "career"
        elif any(word in title for word in ["career", "job", "interview", "workplace"]):
            return "career"

        # Writing/Content creation - based on actual Dev.to tags
        elif any(tag in tags_lower for tag in ["writing", "writers", "blogging", "content"]):
            return "writing"
        elif any(word in title for word in ["writing", "blog", "content creation"]):
            return "writing"

        # Technology/Tools - based on actual Dev.to tags
        elif any(tag in tags_lower for tag in ["technology", "tooling", "tools", "vscode", "webdev"]):
            return "technology"
        elif any(word in title for word in ["technology", "tools", "tech"]):
            return "technology"

        # AI/ML content - based on actual Dev.to tags (very common in this dataset)
        elif any(tag in tags_lower for tag in ["ai", "githubcopilot", "chatgpt", "machinelearning", "ml"]):
            return "ai"
        elif any(word in title for word in ["ai", "artificial intelligence", "copilot", "chatgpt"]):
            return "ai"

        # Productivity content - based on actual Dev.to tags
        elif any(tag in tags_lower for tag in ["productivity", "workflow", "automation", "efficiency"]):
            return "productivity"
        elif any(word in title for word in ["productivity", "workflow", "automation"]):
            return "productivity"

        # Challenge/Contest content - based on actual Dev.to tags
        elif any(tag in tags_lower for tag in ["devchallenge", "challenge", "contest", "hackathon"]):
            return "challenge"
        elif any(word in title for word in ["challenge", "contest", "hackathon"]):
            return "challenge"

        # Mental health content - based on actual Dev.to tags
        elif any(tag in tags_lower for tag in ["mentalhealth", "wellness", "burnout", "health"]):
            return "wellness"
        elif any(word in title for word in ["mental health", "wellness", "burnout"]):
            return "wellness"

        # Default to article for general content
        else:
            return "article"
