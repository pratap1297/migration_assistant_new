"""
Enhanced Git History Analyzer that actually works and provides real commit data
This fixes the "0 commits" issue by using direct git commands
"""
import subprocess
import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict, Counter

# Use centralized LLM configuration
from ..config import get_llm_config, is_llm_available, get_narrative_model

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
    team_velocity: str  # high, medium, low
    recent_activity: str  # active, moderate, inactive
    branch_strategy: str  # git-flow, github-flow, simple
    test_patterns: List[str]
    
class EnhancedGitHistoryAnalyzer:
    """Enhanced Git history analyzer using direct git commands"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        # Use centralized LLM configuration
        self.llm_config = get_llm_config()
        self.llm = get_narrative_model()
        self.gemini_available = is_llm_available()
        
        if self.gemini_available:
            print("OK [GIT-ANALYZER] Gemini LLM initialized successfully")
        else:
            print("WARNING [GIT-ANALYZER] LLM not available - falling back to basic analysis")
        
        # Conventional commit patterns
        self.commit_type_patterns = {
            'feat': r'^feat(\(.+\))?\s*:\s*',
            'fix': r'^fix(\(.+\))?\s*:\s*',
            'docs': r'^docs(\(.+\))?\s*:\s*',
            'style': r'^style(\(.+\))?\s*:\s*',
            'refactor': r'^refactor(\(.+\))?\s*:\s*',
            'test': r'^test(\(.+\))?\s*:\s*',
            'chore': r'^chore(\(.+\))?\s*:\s*',
            'perf': r'^perf(\(.+\))?\s*:\s*',
            'build': r'^build(\(.+\))?\s*:\s*',
            'ci': r'^ci(\(.+\))?\s*:\s*'
        }
        
        # Alternative commit patterns for non-conventional commits
        self.alternative_patterns = {
            'feat': [r'add\s+', r'implement\s+', r'create\s+', r'new\s+'],
            'fix': [r'fix\s+', r'bug\s+', r'resolve\s+', r'correct\s+'],
            'docs': [r'document\s+', r'readme\s+', r'comment\s+'],
            'refactor': [r'refactor\s+', r'cleanup\s+', r'improve\s+'],
            'test': [r'test\s+', r'spec\s+', r'coverage\s+'],
            'chore': [r'update\s+', r'bump\s+', r'dependency\s+', r'maintenance\s+']
        }
        
        # Development patterns to look for
        self.development_patterns = [
            'conventional_commits',
            'feature_branches',
            'hotfix_branches',
            'release_branches',
            'squash_merges',
            'merge_commits',
            'rebase_workflow',
            'pair_programming',
            'frequent_commits',
            'batch_commits',
            'automated_commits',
            'breaking_changes'
        ]
    
    def analyze_git_history(self, repo_path: str) -> GitHistoryInsights:
        """Analyze git history using direct git commands"""
        print(f"INFO [GIT-ANALYZER] Starting git history analysis for {repo_path}")
        
        if not self._is_git_repo(repo_path):
            print(f"WARNING [GIT-ANALYZER] Not a git repository: {repo_path}")
            return self._create_empty_insights()
        
        try:
            # Get basic commit information
            commits = self._get_commits(repo_path)
            print(f"INFO [GIT-ANALYZER] Found {len(commits)} commits")
            
            if not commits:
                print(f"WARNING [GIT-ANALYZER] No commits found in repository")
                return self._create_empty_insights()
            
            # Analyze commits
            commit_analysis = self._analyze_commits(commits)
            
            # Get contributors
            contributors = self._get_contributors(repo_path)
            print(f"INFO [GIT-ANALYZER] Found {len(contributors)} contributors")
            
            # Get file hotspots
            hotspots = self._get_file_hotspots(repo_path)
            print(f"INFO [GIT-ANALYZER] Found {len(hotspots)} file hotspots")
            
            # Analyze development patterns
            patterns = self._analyze_development_patterns(commits, repo_path)
            
            # Create insights
            insights = GitHistoryInsights(
                total_commits=len(commits),
                active_contributors=len(contributors),
                commit_frequency=self._calculate_commit_frequency(commits),
                commit_types=self._analyze_commit_types(commits),
                hotspot_files=hotspots,
                development_patterns=patterns,
                release_cadence=self._determine_release_cadence(commits, repo_path),
                code_stability=self._determine_code_stability(commits, hotspots),
                team_velocity=self._determine_team_velocity(commits),
                recent_activity=self._determine_recent_activity(commits),
                branch_strategy=self._determine_branch_strategy(repo_path),
                test_patterns=self._analyze_test_patterns(commits)
            )
            
            # LLM-ENHANCED: Generate narrative from commit history
            if self.gemini_available and self.llm and commits:
                print("LLM [GIT-ANALYZER] Generating commit narrative with LLM...")
                try:
                    narrative = self._generate_commit_narrative(commits[:100])  # Last 100 commits
                    # Store narrative in development_patterns for now
                    if narrative:
                        insights.development_patterns.append(f"LLM Analysis: {narrative}")
                except Exception as e:
                    print(f"WARNING [GIT-ANALYZER] LLM narrative generation failed: {e}")
            
            print(f"OK [GIT-ANALYZER] Git history analysis completed")
            return insights
            
        except Exception as e:
            print(f"ERROR [GIT-ANALYZER] Error analyzing git history: {e}")
            return self._create_empty_insights()
    
    def _generate_commit_narrative(self, commits: List[Dict[str, Any]]) -> Optional[str]:
        """Generate narrative from commit history using LLM"""
        
        if not commits:
            return None
        
        # Build commit context for LLM
        commit_messages = []
        for commit in commits:
            commit_messages.append({
                'date': commit.get('date', ''),
                'message': commit.get('message', ''),
                'author': commit.get('author', ''),
                'files_changed': len(commit.get('files_changed', [])),
                'insertions': commit.get('insertions', 0),
                'deletions': commit.get('deletions', 0)
            })
        
        # Create prompt
        prompt = f"""
Analyze the following Git commit history and summarize the recent development activity. Focus on development patterns, activity level, and code health.

Recent Commits ({len(commit_messages)} commits):
{json.dumps(commit_messages[:50], indent=2)}  # Limit to 50 for prompt size

Provide a concise summary (2-3 sentences) that covers:
1. Overall development activity level (active, moderate, inactive)
2. Types of changes being made (features, fixes, maintenance)
3. Code health indicators (large changes, frequent fixes, etc.)

Focus on actionable insights for migration planning and team assessment.
"""
        
        try:
            response = self.llm.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"WARNING [GIT-ANALYZER] Error generating narrative: {e}")
            return None
    
    def _is_git_repo(self, repo_path: str) -> bool:
        """Check if the path is a git repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_commits(self, repo_path: str) -> List[Dict[str, Any]]:
        """Get commit information using git log"""
        try:
            # Get commits with detailed information
            result = subprocess.run([
                'git', 'log', '--pretty=format:%H|%an|%ae|%ad|%s|%b', 
                '--date=iso', '--numstat'
            ], cwd=repo_path, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"WARNING [GIT-ANALYZER] Git log failed: {result.stderr}")
                return []
            
            commits = []
            current_commit = None
            
            for line in result.stdout.strip().split('\\n'):
                if '|' in line and len(line.split('|')) >= 5:
                    # New commit line
                    if current_commit:
                        commits.append(current_commit)
                    
                    parts = line.split('|')
                    current_commit = {
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4],
                        'body': parts[5] if len(parts) > 5 else '',
                        'files_changed': [],
                        'insertions': 0,
                        'deletions': 0
                    }
                elif current_commit and '\\t' in line:
                    # File change line (insertions\tdeletions\tfilename)
                    parts = line.split('\\t')
                    if len(parts) >= 3:
                        try:
                            insertions = int(parts[0]) if parts[0] != '-' else 0
                            deletions = int(parts[1]) if parts[1] != '-' else 0
                            filename = parts[2]
                            
                            current_commit['files_changed'].append(filename)
                            current_commit['insertions'] += insertions
                            current_commit['deletions'] += deletions
                        except ValueError:
                            pass
            
            # Add the last commit
            if current_commit:
                commits.append(current_commit)
            
            return commits
            
        except subprocess.TimeoutExpired:
            print(f"WARNING [GIT-ANALYZER] Git log timed out")
            return []
        except Exception as e:
            print(f"WARNING [GIT-ANALYZER] Error getting commits: {e}")
            return []
    
    def _analyze_commits(self, commits: List[Dict[str, Any]]) -> List[CommitAnalysis]:
        """Analyze commits and extract patterns"""
        analyzed_commits = []
        
        for commit in commits:
            try:
                # Parse date with timezone handling
                from datetime import timezone
                date_str = commit['date'].replace('Z', '+00:00')
                date = datetime.fromisoformat(date_str)
                # Ensure date is timezone-aware
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
                
                # Determine commit type
                commit_type = self._determine_commit_type(commit['message'])
                
                analyzed_commit = CommitAnalysis(
                    hash=commit['hash'],
                    author=commit['author'],
                    date=date,
                    message=commit['message'],
                    files_changed=commit['files_changed'],
                    insertions=commit['insertions'],
                    deletions=commit['deletions'],
                    commit_type=commit_type
                )
                
                analyzed_commits.append(analyzed_commit)
                
            except Exception as e:
                print(f"WARNING [GIT-ANALYZER] Error analyzing commit {commit.get('hash', 'unknown')}: {e}")
                continue
        
        return analyzed_commits
    
    def _determine_commit_type(self, message: str) -> str:
        """Determine the type of commit based on the message"""
        message_lower = message.lower()
        
        # Check conventional commit patterns
        for commit_type, pattern in self.commit_type_patterns.items():
            if re.match(pattern, message_lower):
                return commit_type
        
        # Check alternative patterns
        for commit_type, patterns in self.alternative_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return commit_type
        
        return 'other'
    
    def _get_contributors(self, repo_path: str) -> List[Dict[str, Any]]:
        """Get contributor information"""
        try:
            result = subprocess.run([
                'git', 'shortlog', '-sn', '--all'
            ], cwd=repo_path, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
            
            contributors = []
            for line in result.stdout.strip().split('\\n'):
                if line.strip():
                    parts = line.strip().split('\\t')
                    if len(parts) >= 2:
                        contributors.append({
                            'name': parts[1],
                            'commits': int(parts[0])
                        })
            
            return contributors
            
        except Exception as e:
            print(f"WARNING [GIT-ANALYZER] Error getting contributors: {e}")
            return []
    
    def _get_file_hotspots(self, repo_path: str) -> List[FileHotspot]:
        """Get files that change frequently"""
        try:
            result = subprocess.run([
                'git', 'log', '--pretty=format:', '--name-only'
            ], cwd=repo_path, capture_output=True, text=True, timeout=20)
            
            if result.returncode != 0:
                return []
            
            # Count file changes
            file_changes = Counter()
            for line in result.stdout.strip().split('\\n'):
                if line.strip():
                    file_changes[line.strip()] += 1
            
            # Get most frequently changed files
            hotspots = []
            for file_path, frequency in file_changes.most_common(10):
                if frequency > 1:  # Only include files changed more than once
                    # Get last modified date
                    last_modified = self._get_file_last_modified(repo_path, file_path)
                    
                    # Get authors for this file
                    authors = self._get_file_authors(repo_path, file_path)
                    
                    hotspot = FileHotspot(
                        path=file_path,
                        change_frequency=frequency,
                        last_modified=last_modified,
                        authors=authors,
                        complexity_score=min(frequency * 0.1, 1.0)  # Simple complexity score
                    )
                    hotspots.append(hotspot)
            
            return hotspots
            
        except Exception as e:
            print(f"WARNING [GIT-ANALYZER] Error getting file hotspots: {e}")
            return []
    
    def _get_file_last_modified(self, repo_path: str, file_path: str) -> datetime:
        """Get the last modified date of a file"""
        try:
            result = subprocess.run([
                'git', 'log', '-1', '--pretty=format:%ad', '--date=iso', '--', file_path
            ], cwd=repo_path, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                return datetime.fromisoformat(result.stdout.strip().replace('Z', '+00:00'))
            
        except Exception:
            pass
        
        return datetime.now()
    
    def _get_file_authors(self, repo_path: str, file_path: str) -> List[str]:
        """Get authors who modified a file"""
        try:
            result = subprocess.run([
                'git', 'log', '--pretty=format:%an', '--', file_path
            ], cwd=repo_path, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                authors = list(set(result.stdout.strip().split('\\n')))
                return [author for author in authors if author.strip()]
            
        except Exception:
            pass
        
        return []
    
    def _calculate_commit_frequency(self, commits: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate commit frequency over time"""
        frequency = {'daily': 0, 'weekly': 0, 'monthly': 0}
        
        if not commits:
            return frequency
        
        try:
            # Group commits by time periods - use UTC for consistency
            from datetime import timezone
            now = datetime.now(timezone.utc)
            one_day_ago = now - timedelta(days=1)
            one_week_ago = now - timedelta(weeks=1)
            one_month_ago = now - timedelta(days=30)
            
            for commit in commits:
                date_str = commit['date'].replace('Z', '+00:00')
                date = datetime.fromisoformat(date_str)
                # Ensure date is timezone-aware
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
                
                if date >= one_day_ago:
                    frequency['daily'] += 1
                if date >= one_week_ago:
                    frequency['weekly'] += 1
                if date >= one_month_ago:
                    frequency['monthly'] += 1
            
        except Exception as e:
            print(f"WARNING [GIT-ANALYZER] Error calculating commit frequency: {e}")
        
        return frequency
    
    def _analyze_commit_types(self, commits: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze types of commits"""
        commit_types = Counter()
        
        for commit in commits:
            commit_type = self._determine_commit_type(commit['message'])
            commit_types[commit_type] += 1
        
        return dict(commit_types)
    
    def _analyze_development_patterns(self, commits: List[Dict[str, Any]], repo_path: str) -> List[str]:
        """Analyze development patterns"""
        patterns = []
        
        if not commits:
            return patterns
        
        # Check for conventional commits
        conventional_commits = sum(1 for commit in commits 
                                 if any(re.match(pattern, commit['message'].lower()) 
                                       for pattern in self.commit_type_patterns.values()))
        
        if conventional_commits > len(commits) * 0.5:
            patterns.append('conventional_commits')
        
        # Check for frequent commits
        avg_commits_per_week = len(commits) / max(1, self._get_repo_age_weeks(commits))
        if avg_commits_per_week > 10:
            patterns.append('frequent_commits')
        elif avg_commits_per_week < 1:
            patterns.append('batch_commits')
        
        # Check for automated commits
        automated_commits = sum(1 for commit in commits 
                              if any(keyword in commit['message'].lower() 
                                    for keyword in ['automated', 'bot', 'ci', 'build', 'auto']))
        
        if automated_commits > len(commits) * 0.1:
            patterns.append('automated_commits')
        
        return patterns
    
    def _get_repo_age_weeks(self, commits: List[Dict[str, Any]]) -> int:
        """Get repository age in weeks"""
        if not commits:
            return 1
        
        try:
            dates = [datetime.fromisoformat(commit['date'].replace('Z', '+00:00')) for commit in commits]
            oldest_date = min(dates)
            newest_date = max(dates)
            
            age = (newest_date - oldest_date).days / 7
            return max(1, int(age))
            
        except Exception:
            return 1
    
    def _determine_release_cadence(self, commits: List[Dict[str, Any]], repo_path: str) -> str:
        """Determine release cadence"""
        try:
            # Look for tags
            result = subprocess.run([
                'git', 'tag', '--sort=-version:refname'
            ], cwd=repo_path, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                tags = [tag.strip() for tag in result.stdout.strip().split('\\n') if tag.strip()]
                
                if len(tags) >= 2:
                    # Try to determine release pattern
                    tag_dates = []
                    for tag in tags[:5]:  # Check last 5 tags
                        tag_date = self._get_tag_date(repo_path, tag)
                        if tag_date:
                            tag_dates.append(tag_date)
                    
                    if len(tag_dates) >= 2:
                        # Calculate average time between releases
                        intervals = []
                        for i in range(1, len(tag_dates)):
                            interval = (tag_dates[i-1] - tag_dates[i]).days
                            intervals.append(interval)
                        
                        avg_interval = sum(intervals) / len(intervals)
                        
                        if avg_interval <= 7:
                            return 'weekly'
                        elif avg_interval <= 30:
                            return 'monthly'
                        elif avg_interval <= 90:
                            return 'quarterly'
                        else:
                            return 'irregular'
            
        except Exception as e:
            print(f"WARNING [GIT-ANALYZER] Error determining release cadence: {e}")
        
        return 'unknown'
    
    def _get_tag_date(self, repo_path: str, tag: str) -> Optional[datetime]:
        """Get the date of a tag"""
        try:
            result = subprocess.run([
                'git', 'log', '-1', '--pretty=format:%ad', '--date=iso', tag
            ], cwd=repo_path, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                return datetime.fromisoformat(result.stdout.strip().replace('Z', '+00:00'))
            
        except Exception:
            pass
        
        return None
    
    def _determine_code_stability(self, commits: List[Dict[str, Any]], hotspots: List[FileHotspot]) -> str:
        """Determine code stability"""
        if not commits:
            return 'unknown'
        
        # Calculate stability metrics
        avg_changes_per_commit = sum(len(commit['files_changed']) for commit in commits) / len(commits)
        hotspot_count = len(hotspots)
        
        if avg_changes_per_commit < 3 and hotspot_count < 5:
            return 'high'
        elif avg_changes_per_commit < 10 and hotspot_count < 15:
            return 'medium'
        else:
            return 'low'
    
    def _determine_team_velocity(self, commits: List[Dict[str, Any]]) -> str:
        """Determine team velocity"""
        if not commits:
            return 'unknown'
        
        # Calculate recent commit activity
        recent_commits = self._calculate_commit_frequency(commits)
        monthly_commits = recent_commits['monthly']
        
        if monthly_commits > 50:
            return 'high'
        elif monthly_commits > 20:
            return 'medium'
        else:
            return 'low'
    
    def _determine_recent_activity(self, commits: List[Dict[str, Any]]) -> str:
        """Determine recent activity level"""
        if not commits:
            return 'inactive'
        
        recent_commits = self._calculate_commit_frequency(commits)
        
        if recent_commits['weekly'] > 5:
            return 'active'
        elif recent_commits['weekly'] > 1:
            return 'moderate'
        else:
            return 'inactive'
    
    def _determine_branch_strategy(self, repo_path: str) -> str:
        """Determine branch strategy"""
        try:
            result = subprocess.run([
                'git', 'branch', '-a'
            ], cwd=repo_path, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                branches = [branch.strip() for branch in result.stdout.strip().split('\\n')]
                
                # Look for common branch patterns
                has_develop = any('develop' in branch for branch in branches)
                has_main_master = any(branch.endswith(('main', 'master')) for branch in branches)
                has_feature_branches = any('feature/' in branch for branch in branches)
                has_hotfix_branches = any('hotfix/' in branch for branch in branches)
                
                if has_develop and has_feature_branches:
                    return 'git-flow'
                elif has_main_master and has_feature_branches:
                    return 'github-flow'
                else:
                    return 'simple'
            
        except Exception as e:
            print(f"WARNING [GIT-ANALYZER] Error determining branch strategy: {e}")
        
        return 'unknown'
    
    def _analyze_test_patterns(self, commits: List[Dict[str, Any]]) -> List[str]:
        """Analyze testing patterns"""
        patterns = []
        
        test_related_commits = 0
        for commit in commits:
            message = commit['message'].lower()
            if any(keyword in message for keyword in ['test', 'spec', 'coverage', 'tdd', 'bdd']):
                test_related_commits += 1
        
        if test_related_commits > len(commits) * 0.2:
            patterns.append('test_driven_development')
        
        # Check for test files in commits
        test_files = 0
        for commit in commits:
            for file_path in commit['files_changed']:
                if any(keyword in file_path.lower() for keyword in ['test', 'spec', '__test__']):
                    test_files += 1
                    break
        
        if test_files > len(commits) * 0.3:
            patterns.append('comprehensive_testing')
        
        return patterns
    
    def _create_empty_insights(self) -> GitHistoryInsights:
        """Create empty insights when git analysis fails"""
        return GitHistoryInsights(
            total_commits=0,
            active_contributors=0,
            commit_frequency={'daily': 0, 'weekly': 0, 'monthly': 0},
            commit_types={},
            hotspot_files=[],
            development_patterns=[],
            release_cadence='unknown',
            code_stability='unknown',
            team_velocity='unknown',
            recent_activity='unknown',
            branch_strategy='unknown',
            test_patterns=[]
        )