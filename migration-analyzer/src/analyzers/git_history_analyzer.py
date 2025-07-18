"""
Git History Analyzer for extracting development patterns and metadata
"""
import subprocess
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
try:
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    Repo = None
from collections import defaultdict, Counter

@dataclass
class CommitAnalysis:
    """Analysis of a single commit"""
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int
    commit_type: str  # feat, fix, docs, refactor, etc.
    
@dataclass
class FileHotspot:
    """Information about a frequently changed file"""
    path: str
    change_frequency: int
    last_modified: datetime
    authors: List[str]
    complexity_score: float
    
@dataclass
class GitHistoryInsights:
    """Insights extracted from git history"""
    total_commits: int
    active_contributors: int
    commit_frequency: Dict[str, int]  # commits per week/month
    commit_types: Dict[str, int]  # feat, fix, docs, etc.
    hotspot_files: List[FileHotspot]
    development_patterns: List[str]
    release_cadence: str
    code_stability: str  # high, medium, low
    team_velocity: Dict[str, Any]

class GitHistoryAnalyzer:
    """Analyzer for git history and development patterns"""
    
    def __init__(self):
        self.commit_type_patterns = {
            'feat': [r'^feat(\(.+\))?\s*:', r'^feature\s*:', r'^add\s+'],
            'fix': [r'^fix(\(.+\))?\s*:', r'^bug\s*:', r'^hotfix\s*:'],
            'docs': [r'^docs?(\(.+\))?\s*:', r'^documentation\s*:', r'^readme\s*:'],
            'refactor': [r'^refactor(\(.+\))?\s*:', r'^refactoring\s*:', r'^cleanup\s*:'],
            'test': [r'^test(\(.+\))?\s*:', r'^testing\s*:', r'^spec\s*:'],
            'chore': [r'^chore(\(.+\))?\s*:', r'^maintenance\s*:', r'^update\s+'],
            'style': [r'^style(\(.+\))?\s*:', r'^formatting\s*:', r'^linting\s*:'],
            'perf': [r'^perf(\(.+\))?\s*:', r'^performance\s*:', r'^optimization\s*:'],
            'ci': [r'^ci(\(.+\))?\s*:', r'^build\s*:', r'^deploy\s*:'],
            'security': [r'^security(\(.+\))?\s*:', r'^sec\s*:', r'^vulnerability\s*:']
        }
    
    def analyze_git_history(self, repo_path: str, days_back: int = 365) -> GitHistoryInsights:
        """Analyze git history for development patterns"""
        if not GIT_AVAILABLE:
            return self._create_empty_insights()
        
        try:
            repo = Repo(repo_path)
            
            # Get commits from the specified time period
            since_date = datetime.now() - timedelta(days=days_back)
            commits = list(repo.iter_commits(since=since_date))
            
            if not commits:
                return self._create_empty_insights()
            
            # Analyze commits
            commit_analyses = []
            for commit in commits:
                try:
                    analysis = self._analyze_commit(commit)
                    commit_analyses.append(analysis)
                except Exception as e:
                    print(f"Error analyzing commit {commit.hexsha}: {e}")
                    continue
            
            # Generate insights
            insights = self._generate_insights(commit_analyses, repo_path)
            return insights
            
        except Exception as e:
            print(f"Error analyzing git history: {e}")
            return self._create_empty_insights()
    
    def _analyze_commit(self, commit) -> CommitAnalysis:
        """Analyze a single commit"""
        # Get commit stats
        stats = commit.stats
        total_insertions = stats.total.get('insertions', 0)
        total_deletions = stats.total.get('deletions', 0)
        
        # Get changed files
        files_changed = list(stats.files.keys())
        
        # Classify commit type
        commit_type = self._classify_commit_type(commit.message)
        
        return CommitAnalysis(
            hash=commit.hexsha,
            author=commit.author.name,
            date=commit.committed_datetime,
            message=commit.message.strip(),
            files_changed=files_changed,
            insertions=total_insertions,
            deletions=total_deletions,
            commit_type=commit_type
        )
    
    def _classify_commit_type(self, commit_message: str) -> str:
        """Classify commit type based on message"""
        message_lower = commit_message.lower()
        
        for commit_type, patterns in self.commit_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return commit_type
        
        return 'other'
    
    def _generate_insights(self, commit_analyses: List[CommitAnalysis], repo_path: str) -> GitHistoryInsights:
        """Generate insights from commit analyses"""
        
        # Basic statistics
        total_commits = len(commit_analyses)
        authors = set(c.author for c in commit_analyses)
        active_contributors = len(authors)
        
        # Commit frequency analysis
        commit_dates = [c.date for c in commit_analyses]
        commit_frequency = self._calculate_commit_frequency(commit_dates)
        
        # Commit type distribution
        commit_types = Counter(c.commit_type for c in commit_analyses)
        
        # File hotspots
        hotspot_files = self._identify_hotspots(commit_analyses)
        
        # Development patterns
        development_patterns = self._identify_development_patterns(commit_analyses)
        
        # Release cadence
        release_cadence = self._determine_release_cadence(commit_analyses)
        
        # Code stability
        code_stability = self._assess_code_stability(commit_analyses)
        
        # Team velocity
        team_velocity = self._calculate_team_velocity(commit_analyses)
        
        return GitHistoryInsights(
            total_commits=total_commits,
            active_contributors=active_contributors,
            commit_frequency=commit_frequency,
            commit_types=dict(commit_types),
            hotspot_files=hotspot_files,
            development_patterns=development_patterns,
            release_cadence=release_cadence,
            code_stability=code_stability,
            team_velocity=team_velocity
        )
    
    def _calculate_commit_frequency(self, commit_dates: List[datetime]) -> Dict[str, int]:
        """Calculate commit frequency patterns"""
        if not commit_dates:
            return {}
        
        # Group by week
        week_counts = defaultdict(int)
        for date in commit_dates:
            week_start = date - timedelta(days=date.weekday())
            week_key = week_start.strftime('%Y-W%U')
            week_counts[week_key] += 1
        
        # Calculate average
        total_weeks = len(week_counts)
        avg_commits_per_week = sum(week_counts.values()) / total_weeks if total_weeks > 0 else 0
        
        # Group by day of week
        weekday_counts = defaultdict(int)
        for date in commit_dates:
            weekday = date.strftime('%A')
            weekday_counts[weekday] += 1
        
        return {
            'average_commits_per_week': round(avg_commits_per_week, 2),
            'most_active_weekday': max(weekday_counts.items(), key=lambda x: x[1])[0] if weekday_counts else 'Unknown',
            'total_weeks': total_weeks,
            'weekday_distribution': dict(weekday_counts)
        }
    
    def _identify_hotspots(self, commit_analyses: List[CommitAnalysis]) -> List[FileHotspot]:
        """Identify frequently changed files (hotspots)"""
        file_changes = defaultdict(list)
        
        for commit in commit_analyses:
            for file_path in commit.files_changed:
                file_changes[file_path].append(commit)
        
        hotspots = []
        for file_path, commits in file_changes.items():
            if len(commits) >= 5:  # Only consider files changed 5+ times
                authors = list(set(c.author for c in commits))
                last_modified = max(c.date for c in commits)
                
                # Calculate complexity score based on change frequency and recency
                days_since_last_change = (datetime.now() - last_modified.replace(tzinfo=None)).days
                complexity_score = len(commits) * (1 / (1 + days_since_last_change / 30))
                
                hotspot = FileHotspot(
                    path=file_path,
                    change_frequency=len(commits),
                    last_modified=last_modified,
                    authors=authors,
                    complexity_score=complexity_score
                )
                hotspots.append(hotspot)
        
        # Sort by complexity score (descending)
        hotspots.sort(key=lambda x: x.complexity_score, reverse=True)
        return hotspots[:10]  # Return top 10 hotspots
    
    def _identify_development_patterns(self, commit_analyses: List[CommitAnalysis]) -> List[str]:
        """Identify development patterns from commit history"""
        patterns = []
        
        # Check for conventional commits
        conventional_commits = sum(1 for c in commit_analyses if c.commit_type != 'other')
        if conventional_commits / len(commit_analyses) > 0.6:
            patterns.append("Uses conventional commit messages")
        
        # Check for frequent small commits vs large commits
        avg_files_per_commit = sum(len(c.files_changed) for c in commit_analyses) / len(commit_analyses)
        if avg_files_per_commit < 3:
            patterns.append("Prefers small, focused commits")
        elif avg_files_per_commit > 10:
            patterns.append("Tends to make large, multi-file commits")
        
        # Check for test-driven development
        test_commits = sum(1 for c in commit_analyses if c.commit_type == 'test')
        if test_commits > 0 and test_commits / len(commit_analyses) > 0.15:
            patterns.append("Shows evidence of test-driven development")
        
        # Check for documentation practices
        doc_commits = sum(1 for c in commit_analyses if c.commit_type == 'docs')
        if doc_commits > 0 and doc_commits / len(commit_analyses) > 0.1:
            patterns.append("Regularly updates documentation")
        
        # Check for refactoring practices
        refactor_commits = sum(1 for c in commit_analyses if c.commit_type == 'refactor')
        if refactor_commits > 0 and refactor_commits / len(commit_analyses) > 0.1:
            patterns.append("Regular refactoring and code cleanup")
        
        return patterns
    
    def _determine_release_cadence(self, commit_analyses: List[CommitAnalysis]) -> str:
        """Determine release cadence from commit patterns"""
        # Look for version tags or release-related commits
        release_commits = []
        for commit in commit_analyses:
            message_lower = commit.message.lower()
            if any(keyword in message_lower for keyword in ['release', 'version', 'v1.', 'v2.', 'tag']):
                release_commits.append(commit)
        
        if not release_commits:
            return "No clear release pattern"
        
        # Calculate time between releases
        if len(release_commits) >= 2:
            release_dates = sorted([c.date for c in release_commits])
            intervals = []
            for i in range(1, len(release_dates)):
                interval = (release_dates[i] - release_dates[i-1]).days
                intervals.append(interval)
            
            avg_interval = sum(intervals) / len(intervals)
            
            if avg_interval <= 7:
                return "Weekly releases"
            elif avg_interval <= 14:
                return "Bi-weekly releases"
            elif avg_interval <= 30:
                return "Monthly releases"
            elif avg_interval <= 90:
                return "Quarterly releases"
            else:
                return "Infrequent releases"
        
        return "Single release detected"
    
    def _assess_code_stability(self, commit_analyses: List[CommitAnalysis]) -> str:
        """Assess code stability based on commit patterns"""
        if not commit_analyses:
            return "unknown"
        
        # Calculate fix-to-feature ratio
        fix_commits = sum(1 for c in commit_analyses if c.commit_type == 'fix')
        feature_commits = sum(1 for c in commit_analyses if c.commit_type == 'feat')
        
        if feature_commits == 0:
            fix_ratio = 1.0
        else:
            fix_ratio = fix_commits / feature_commits
        
        # Calculate churn (lines changed per commit)
        total_changes = sum(c.insertions + c.deletions for c in commit_analyses)
        avg_churn = total_changes / len(commit_analyses)
        
        # Determine stability
        if fix_ratio > 0.5 or avg_churn > 500:
            return "low"
        elif fix_ratio > 0.3 or avg_churn > 200:
            return "medium"
        else:
            return "high"
    
    def _calculate_team_velocity(self, commit_analyses: List[CommitAnalysis]) -> Dict[str, Any]:
        """Calculate team velocity metrics"""
        if not commit_analyses:
            return {}
        
        # Group commits by author
        author_commits = defaultdict(list)
        for commit in commit_analyses:
            author_commits[commit.author].append(commit)
        
        # Calculate per-author metrics
        author_metrics = {}
        for author, commits in author_commits.items():
            total_changes = sum(c.insertions + c.deletions for c in commits)
            avg_changes_per_commit = total_changes / len(commits)
            
            author_metrics[author] = {
                'commits': len(commits),
                'total_changes': total_changes,
                'avg_changes_per_commit': round(avg_changes_per_commit, 2)
            }
        
        # Calculate team metrics
        total_changes = sum(c.insertions + c.deletions for c in commit_analyses)
        
        return {
            'team_size': len(author_commits),
            'total_commits': len(commit_analyses),
            'total_changes': total_changes,
            'avg_changes_per_commit': round(total_changes / len(commit_analyses), 2),
            'author_metrics': author_metrics,
            'most_active_contributor': max(author_commits.items(), key=lambda x: len(x[1]))[0]
        }
    
    def _create_empty_insights(self) -> GitHistoryInsights:
        """Create empty insights when git history is not available"""
        return GitHistoryInsights(
            total_commits=0,
            active_contributors=0,
            commit_frequency={},
            commit_types={},
            hotspot_files=[],
            development_patterns=[],
            release_cadence="Unknown",
            code_stability="unknown",
            team_velocity={}
        )