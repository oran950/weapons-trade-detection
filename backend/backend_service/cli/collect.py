"""
CLI for data collection operations
"""
import argparse
import asyncio
import sys
from datetime import datetime
from typing import List, Optional


class CollectionCLI:
    """
    Command-line interface for data collection
    """
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog="collect",
            description="Collect data from Reddit or Telegram for analysis"
        )
        
        subparsers = parser.add_subparsers(dest="platform", help="Platform to collect from")
        
        # Reddit subcommand
        reddit_parser = subparsers.add_parser("reddit", help="Collect from Reddit")
        reddit_parser.add_argument(
            "-s", "--subreddits",
            nargs="+",
            default=["news"],
            help="Subreddits to collect from"
        )
        reddit_parser.add_argument(
            "-t", "--time-filter",
            choices=["hour", "day", "week", "month", "year", "all"],
            default="day",
            help="Time filter for posts"
        )
        reddit_parser.add_argument(
            "-m", "--sort-method",
            choices=["hot", "new", "top", "rising"],
            default="hot",
            help="Sort method for posts"
        )
        reddit_parser.add_argument(
            "-l", "--limit",
            type=int,
            default=25,
            help="Number of posts per subreddit"
        )
        reddit_parser.add_argument(
            "-k", "--keywords",
            nargs="+",
            default=[],
            help="Keywords to search for"
        )
        reddit_parser.add_argument(
            "--all-defaults",
            action="store_true",
            help="Use default subreddit list"
        )
        reddit_parser.add_argument(
            "--analyze",
            action="store_true",
            help="Analyze collected posts"
        )
        reddit_parser.add_argument(
            "-o", "--output",
            help="Output filename (without extension)"
        )
        
        # Telegram subcommand
        telegram_parser = subparsers.add_parser("telegram", help="Collect from Telegram")
        telegram_parser.add_argument(
            "-c", "--channels",
            nargs="+",
            default=[],
            help="Channel usernames to collect from"
        )
        telegram_parser.add_argument(
            "-g", "--groups",
            nargs="+",
            type=int,
            default=[],
            help="Group IDs to collect from"
        )
        telegram_parser.add_argument(
            "-k", "--keywords",
            nargs="+",
            default=[],
            help="Keywords to search for"
        )
        telegram_parser.add_argument(
            "-l", "--limit",
            type=int,
            default=50,
            help="Number of messages per source"
        )
        telegram_parser.add_argument(
            "--search-global",
            action="store_true",
            help="Search across all accessible chats"
        )
        telegram_parser.add_argument(
            "--analyze",
            action="store_true",
            help="Analyze collected messages"
        )
        telegram_parser.add_argument(
            "-o", "--output",
            help="Output filename (without extension)"
        )
        
        return parser
    
    def run(self, args: List[str] = None):
        """
        Run the CLI
        
        Args:
            args: Command-line arguments (uses sys.argv if None)
        """
        parsed = self.parser.parse_args(args)
        
        if not parsed.platform:
            self.parser.print_help()
            return
        
        if parsed.platform == "reddit":
            self._collect_reddit(parsed)
        elif parsed.platform == "telegram":
            asyncio.run(self._collect_telegram(parsed))
    
    def _collect_reddit(self, args):
        """Collect from Reddit"""
        from ..config import config
        from ..handlers.reddit_handler import RedditHandler
        
        if not config.reddit_configured:
            print("Error: Reddit API not configured")
            print(f"Missing: {', '.join(config.get_missing_reddit_config())}")
            sys.exit(1)
        
        print("Initializing Reddit collector...")
        handler = RedditHandler(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT,
            data_dir=config.DATA_DIR
        )
        
        # Determine subreddits
        if args.all_defaults:
            subreddits = [
                "news", "worldnews", "politics", "guns", "firearms",
                "CCW", "ar15", "ak47", "gundeals", "gunpolitics",
                "Military", "army", "navy", "airforce", "marines"
            ]
        else:
            subreddits = args.subreddits
        
        print(f"Collecting from {len(subreddits)} subreddits...")
        
        all_posts = []
        for subreddit in subreddits:
            if args.keywords:
                posts = handler.search_posts_by_keywords(
                    subreddit, args.keywords, args.time_filter, args.limit
                )
            else:
                posts = handler.collect_subreddit_posts(
                    subreddit, args.time_filter, args.limit, args.sort_method
                )
            all_posts.extend(posts)
        
        print(f"Total collected: {len(all_posts)} posts")
        
        # Analyze if requested
        if args.analyze:
            print("Analyzing posts...")
            all_posts = handler.analyze_posts(all_posts)
        
        # Generate filename
        if args.output:
            filename = args.output
        else:
            filename = f"reddit_{args.time_filter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save
        files = handler.save_posts(all_posts, f"{filename}_raw")
        print(f"Saved to: {files}")
        
        if args.analyze:
            summary = handler.save_analyzed_posts(all_posts, filename)
            print(f"High risk: {summary['analysis_info']['high_risk_count']}")
            print(f"Medium risk: {summary['analysis_info']['medium_risk_count']}")
            print(f"Low risk: {summary['analysis_info']['low_risk_count']}")
    
    async def _collect_telegram(self, args):
        """Collect from Telegram"""
        from ..config import config
        from ..handlers.telegram_handler import TelegramHandler
        
        if not config.telegram_configured:
            print("Error: Telegram API not configured")
            print(f"Missing: {', '.join(config.get_missing_telegram_config())}")
            sys.exit(1)
        
        print("Initializing Telegram collector...")
        handler = TelegramHandler(
            api_id=config.TELEGRAM_API_ID,
            api_hash=config.TELEGRAM_API_HASH,
            data_dir=config.DATA_DIR
        )
        
        if not await handler.connect():
            print("Error: Failed to connect to Telegram")
            sys.exit(1)
        
        all_messages = []
        
        # Collect from channels
        for channel in args.channels:
            print(f"Collecting from @{channel}...")
            messages = await handler.collect_channel_messages(channel, args.limit)
            all_messages.extend(messages)
        
        # Collect from groups
        for group_id in args.groups:
            print(f"Collecting from group {group_id}...")
            messages = await handler.collect_group_messages(group_id, args.limit)
            all_messages.extend(messages)
        
        # Search by keywords
        if args.search_global and args.keywords:
            for keyword in args.keywords:
                print(f"Searching for '{keyword}'...")
                messages = await handler.search_messages(keyword, args.limit)
                all_messages.extend(messages)
        
        await handler.disconnect()
        
        print(f"Total collected: {len(all_messages)} messages")
        
        # Analyze if requested
        if args.analyze:
            print("Analyzing messages...")
            all_messages = handler.analyze_messages(all_messages)
        
        # Generate filename
        if args.output:
            filename = args.output
        else:
            filename = f"telegram_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save
        files = handler.save_messages(all_messages, filename)
        print(f"Saved to: {files}")


def main():
    """Main entry point"""
    cli = CollectionCLI()
    cli.run()


if __name__ == "__main__":
    main()

