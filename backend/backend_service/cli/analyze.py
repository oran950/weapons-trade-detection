"""
CLI for batch analysis operations
"""
import argparse
import json
import sys
from datetime import datetime
from typing import List, Optional
from pathlib import Path


class AnalysisCLI:
    """
    Command-line interface for batch analysis
    """
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog="analyze",
            description="Analyze collected data for weapons trade indicators"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Analysis command")
        
        # Analyze file
        file_parser = subparsers.add_parser("file", help="Analyze a collected data file")
        file_parser.add_argument(
            "input_file",
            help="Path to JSON file with collected data"
        )
        file_parser.add_argument(
            "-o", "--output",
            help="Output filename (without extension)"
        )
        file_parser.add_argument(
            "--use-llm",
            action="store_true",
            help="Use LLM for enhanced analysis"
        )
        file_parser.add_argument(
            "--high-risk-only",
            action="store_true",
            help="Only output high-risk posts"
        )
        
        # Analyze text
        text_parser = subparsers.add_parser("text", help="Analyze a single text")
        text_parser.add_argument(
            "text",
            help="Text to analyze"
        )
        text_parser.add_argument(
            "--use-llm",
            action="store_true",
            help="Use LLM for enhanced analysis"
        )
        text_parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Show detailed output"
        )
        
        # Batch analyze
        batch_parser = subparsers.add_parser("batch", help="Analyze multiple files")
        batch_parser.add_argument(
            "directory",
            help="Directory containing JSON files"
        )
        batch_parser.add_argument(
            "-o", "--output-dir",
            help="Output directory for results"
        )
        batch_parser.add_argument(
            "--pattern",
            default="*_raw.json",
            help="File pattern to match"
        )
        
        # Summary
        summary_parser = subparsers.add_parser("summary", help="Generate summary from analyzed files")
        summary_parser.add_argument(
            "directory",
            help="Directory containing analyzed JSON files"
        )
        summary_parser.add_argument(
            "-o", "--output",
            help="Output filename for summary"
        )
        
        return parser
    
    def run(self, args: List[str] = None):
        """
        Run the CLI
        
        Args:
            args: Command-line arguments (uses sys.argv if None)
        """
        parsed = self.parser.parse_args(args)
        
        if not parsed.command:
            self.parser.print_help()
            return
        
        if parsed.command == "file":
            self._analyze_file(parsed)
        elif parsed.command == "text":
            self._analyze_text(parsed)
        elif parsed.command == "batch":
            self._analyze_batch(parsed)
        elif parsed.command == "summary":
            self._generate_summary(parsed)
    
    def _analyze_file(self, args):
        """Analyze a single file"""
        from ..handlers.analysis_handler import AnalysisHandler
        from ..entities.post import RedditPost, TelegramMessage
        from dataclasses import asdict
        
        input_path = Path(args.input_file)
        
        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            sys.exit(1)
        
        print(f"Loading {input_path}...")
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Determine post type and extract posts
        posts_data = data.get('posts', data.get('messages', []))
        if not posts_data:
            print("Error: No posts found in file")
            sys.exit(1)
        
        # Convert to post objects
        posts = []
        for p in posts_data:
            if 'subreddit' in p:
                # Reddit post
                post = RedditPost(
                    id=p.get('id', ''),
                    title=p.get('title', ''),
                    content=p.get('content', ''),
                    subreddit=p.get('subreddit', ''),
                    author_hash=p.get('author_hash', ''),
                    score=p.get('score', 0),
                    num_comments=p.get('num_comments', 0),
                    created_at=p.get('created_at', p.get('created_utc', 0)),
                    url=p.get('url', ''),
                    collected_at=p.get('collected_at', ''),
                    platform='reddit'
                )
            else:
                # Telegram message
                post = TelegramMessage(
                    id=p.get('id', ''),
                    content=p.get('content', ''),
                    author_hash=p.get('author_hash', ''),
                    chat_id=p.get('chat_id', 0),
                    chat_title=p.get('chat_title', ''),
                    chat_type=p.get('chat_type', ''),
                    created_at=p.get('created_at', 0),
                    url=p.get('url', ''),
                    collected_at=p.get('collected_at', ''),
                    platform='telegram'
                )
            posts.append(post)
        
        print(f"Loaded {len(posts)} posts")
        
        # Initialize handler
        handler = AnalysisHandler(use_llm=args.use_llm)
        
        # Analyze
        print("Analyzing posts...")
        analyzed = handler.analyze_posts_batch(posts)
        
        # Generate output filename
        if args.output:
            output_name = args.output
        else:
            output_name = input_path.stem.replace('_raw', '') + '_analyzed'
        
        # Save results
        summary = handler.save_analysis_results(analyzed, output_name)
        
        # Print summary
        print("\n" + "=" * 50)
        print("ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"Total posts: {summary['total_posts']}")
        print(f"High risk: {summary['risk_distribution']['high_risk']}")
        print(f"Medium risk: {summary['risk_distribution']['medium_risk']}")
        print(f"Low risk: {summary['risk_distribution']['low_risk']}")
        print(f"High risk %: {summary['risk_distribution']['high_risk_percentage']}%")
        print("=" * 50)
    
    def _analyze_text(self, args):
        """Analyze a single text"""
        from ..core.detector import WeaponsDetector
        
        detector = WeaponsDetector(use_llm=args.use_llm)
        assessment = detector.analyze(args.text, use_llm_override=args.use_llm)
        
        result = assessment.result
        
        print("\n" + "=" * 50)
        print("ANALYSIS RESULT")
        print("=" * 50)
        print(f"Risk Score: {result.risk_score:.3f}")
        print(f"Risk Level: {result.risk_level}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Source: {result.source}")
        
        if args.verbose:
            print("\nFlags:")
            for flag in result.flags:
                print(f"  - {flag}")
            
            print("\nKeywords:")
            for kw in result.detected_keywords:
                print(f"  - {kw}")
            
            print("\nPatterns:")
            for pat in result.detected_patterns:
                print(f"  - {pat}")
            
            if result.llm_reasons:
                print("\nLLM Reasons:")
                for reason in result.llm_reasons:
                    print(f"  - {reason}")
        
        print("=" * 50)
    
    def _analyze_batch(self, args):
        """Analyze multiple files"""
        from ..handlers.analysis_handler import AnalysisHandler
        from glob import glob
        
        input_dir = Path(args.directory)
        
        if not input_dir.exists():
            print(f"Error: Directory not found: {input_dir}")
            sys.exit(1)
        
        # Find files
        pattern = str(input_dir / args.pattern)
        files = glob(pattern)
        
        if not files:
            print(f"No files matching pattern: {args.pattern}")
            return
        
        print(f"Found {len(files)} files to analyze")
        
        for filepath in files:
            print(f"\nProcessing: {filepath}")
            # Use file analysis for each
            fake_args = argparse.Namespace(
                input_file=filepath,
                output=None,
                use_llm=False,
                high_risk_only=False
            )
            self._analyze_file(fake_args)
    
    def _generate_summary(self, args):
        """Generate summary from analyzed files"""
        from glob import glob
        
        input_dir = Path(args.directory)
        
        if not input_dir.exists():
            print(f"Error: Directory not found: {input_dir}")
            sys.exit(1)
        
        # Find analyzed files
        files = glob(str(input_dir / "*_analyzed.json"))
        
        if not files:
            print("No analyzed files found")
            return
        
        total_posts = 0
        total_high = 0
        total_medium = 0
        total_low = 0
        all_keywords = []
        
        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'analysis_info' in data:
                info = data['analysis_info']
                total_posts += info.get('total_posts', 0)
                total_high += info.get('high_risk_count', len(data.get('high_risk_posts', [])))
                total_medium += info.get('medium_risk_count', len(data.get('medium_risk_posts', [])))
                total_low += info.get('low_risk_count', len(data.get('low_risk_posts', [])))
        
        summary = {
            "summary_timestamp": datetime.now().isoformat(),
            "files_analyzed": len(files),
            "total_posts": total_posts,
            "total_high_risk": total_high,
            "total_medium_risk": total_medium,
            "total_low_risk": total_low,
            "high_risk_percentage": round(total_high / total_posts * 100, 2) if total_posts > 0 else 0
        }
        
        print("\n" + "=" * 50)
        print("AGGREGATE SUMMARY")
        print("=" * 50)
        for key, value in summary.items():
            print(f"{key}: {value}")
        print("=" * 50)
        
        # Save if output specified
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            print(f"\nSaved to: {output_path}")


def main():
    """Main entry point"""
    cli = AnalysisCLI()
    cli.run()


if __name__ == "__main__":
    main()

