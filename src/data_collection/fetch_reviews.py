#!/usr/bin/env python3
"""
Enhanced Review Fetcher for Consumer Security Analysis

This module provides improved functionality for fetching app reviews from 
Google Play Store and Apple App Store with better error handling, 
data validation, and security analysis features.

Author: Your Name
Version: 2.0
"""

import os
import sys
import pandas as pd
import argparse
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import time
import json

# Third-party imports
try:
    from google_play_scraper import Sort, reviews as gp_reviews
    from app_store_web_scraper import AppStoreEntry
except ImportError as e:
    print(f"Error: Missing required packages. Please install: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project structure setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

# Ensure directories exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Security-related keywords for filtering
SECURITY_KEYWORDS = [
    'security', 'privacy', 'secure', 'private', 'data', 'password', 
    'login', 'account', 'hack', 'breach', 'steal', 'fraud', 'scam',
    'phishing', 'malware', 'virus', 'encrypt', 'decrypt', 'biometric',
    'fingerprint', 'face id', 'two factor', '2fa', 'authentication',
    'permissions', 'access', 'tracking', 'surveillance', 'leak'
]

class ReviewFetcher:
    """Enhanced review fetcher with improved functionality."""
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize the review fetcher.
        
        Args:
            delay: Delay between requests to respect rate limits
        """
        self.delay = delay
        self.stats = {'fetched': 0, 'errors': 0, 'security_related': 0}
    
    def fetch_google_reviews(
        self, 
        app_id: str, 
        lang: str = "en", 
        country: str = "us", 
        max_reviews: int = 10000,
        sort_by: Sort = Sort.NEWEST
    ) -> pd.DataFrame:
        """
        Fetch reviews from Google Play Store with enhanced error handling.
        """
        logger.info(f"Starting Google Play reviews fetch for {app_id}")
        logger.info(f"Parameters: lang={lang}, country={country}, max_reviews={max_reviews}")
        
        all_reviews = []
        token = None
        batch_size = 200
        
        try:
            while len(all_reviews) < max_reviews:
                batch_count = min(batch_size, max_reviews - len(all_reviews))
                
                logger.info(f"Fetching batch: {len(all_reviews) + 1}-{len(all_reviews) + batch_count}")
                
                try:
                    result, token = gp_reviews(
                        app_id,
                        lang=lang,
                        country=country,
                        sort=sort_by,
                        count=batch_count,
                        continuation_token=token
                    )
                    
                    if not result:
                        logger.info("No more reviews available")
                        break
                    
                    all_reviews.extend(result)
                    self.stats['fetched'] += len(result)
                    
                    logger.info(f"✅ Fetched {len(result)} reviews. Total: {len(all_reviews)}")
                    
                    # Respect rate limits
                    if self.delay > 0:
                        time.sleep(self.delay)
                    
                    if token is None:
                        logger.info("Reached end of available reviews")
                        break
                        
                except Exception as e:
                    logger.error(f"Error fetching batch: {e}")
                    self.stats['errors'] += 1
                    time.sleep(self.delay * 2)
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Fetch interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error during fetch: {e}")
            
        if not all_reviews:
            logger.warning("No reviews were fetched")
            return pd.DataFrame()
        
        # Convert to DataFrame and validate
        df = self._process_google_data(all_reviews)
        logger.info(f"✅ Successfully processed {len(df)} Google Play reviews")
        
        return df
    
    def fetch_apple_reviews(
        self, 
        app_id: str, 
        country: str = "us", 
        max_reviews: int = 10000
    ) -> pd.DataFrame:
        """
        Fetch reviews from Apple App Store with enhanced error handling.
        """
        logger.info(f"Starting Apple App Store reviews fetch for app ID {app_id}")
        logger.info(f"Parameters: country={country}, max_reviews={max_reviews}")
        
        reviews = []
        
        try:
            app = AppStoreEntry(app_id=int(app_id), country=country.lower())
            
            for idx, review in enumerate(app.reviews()):
                if len(reviews) >= max_reviews:
                    logger.info("Reached maximum review limit")
                    break
                
                review_data = {
                    "reviewId": review.id,
                    "userName": review.user_name,
                    "content": review.review,
                    "score": review.rating,
                    "at": review.date
                }
                
                reviews.append(review_data)
                self.stats['fetched'] += 1
                
                # Log progress every 100 reviews
                if (idx + 1) % 100 == 0:
                    logger.info(f"✅ Fetched {idx + 1} reviews...")
                
                # Respect rate limits
                if self.delay > 0 and idx % 10 == 0:
                    time.sleep(self.delay / 10)
                    
        except KeyboardInterrupt:
            logger.info("Fetch interrupted by user")
        except Exception as e:
            logger.error(f"Error fetching Apple reviews: {e}")
            self.stats['errors'] += 1
        
        if not reviews:
            logger.warning("No Apple reviews were fetched")
            return pd.DataFrame()
        
        # Convert to DataFrame and validate
        df = self._process_apple_data(reviews)
        logger.info(f"✅ Successfully processed {len(df)} Apple App Store reviews")
        
        return df
    
    def _process_google_data(self, reviews: List[Dict]) -> pd.DataFrame:
        """Process and validate Google Play review data."""
        try:
            df = pd.DataFrame(reviews)
            
            # Validate required columns
            required_cols = ['reviewId', 'userName', 'content', 'score', 'at']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return pd.DataFrame()
            
            # Clean and validate data
            df['at'] = pd.to_datetime(df['at'])
            df['content'] = df['content'].fillna('')
            df['userName'] = df['userName'].fillna('Anonymous')
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
            
            # Remove invalid scores
            df = df[df['score'].between(1, 5)]
            
            # Add metadata
            df['platform'] = 'google'
            df['fetched_at'] = datetime.now()
            
            # Flag security-related reviews
            df['is_security_related'] = df['content'].str.lower().str.contains(
                '|'.join(SECURITY_KEYWORDS), na=False
            )
            
            self.stats['security_related'] = df['is_security_related'].sum()
            
            return df[required_cols + ['platform', 'fetched_at', 'is_security_related']]
            
        except Exception as e:
            logger.error(f"Error processing Google data: {e}")
            return pd.DataFrame()
    
    def _process_apple_data(self, reviews: List[Dict]) -> pd.DataFrame:
        """Process and validate Apple App Store review data."""
        try:
            df = pd.DataFrame(reviews)
            
            if df.empty:
                return df
            
            # Clean and validate data
            df['at'] = pd.to_datetime(df['at'])
            df['content'] = df['content'].fillna('')
            df['userName'] = df['userName'].fillna('Anonymous')
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
            
            # Remove invalid scores
            df = df[df['score'].between(1, 5)]
            
            # Add metadata
            df['platform'] = 'apple'
            df['fetched_at'] = datetime.now()
            
            # Flag security-related reviews
            df['is_security_related'] = df['content'].str.lower().str.contains(
                '|'.join(SECURITY_KEYWORDS), na=False
            )
            
            self.stats['security_related'] = df['is_security_related'].sum()
            
            return df[['reviewId', 'userName', 'content', 'score', 'at', 
                      'platform', 'fetched_at', 'is_security_related']]
            
        except Exception as e:
            logger.error(f"Error processing Apple data: {e}")
            return pd.DataFrame()
    
    def save_reviews(self, df: pd.DataFrame, filename: str, 
                    save_processed: bool = True) -> str:
        """
        Save reviews to CSV with optional processed version.
        """
        if df.empty:
            logger.warning("No data to save")
            return ""
        
        # Save raw data
        raw_path = os.path.join(RAW_DIR, f"{filename}.csv")
        df.to_csv(raw_path, index=False)
        logger.info(f"✅ Raw data saved to: {raw_path}")
        
        if save_processed:
            # Save processed version with additional analysis
            processed_df = df.copy()
            
            # Add basic statistics
            processed_df['content_length'] = processed_df['content'].str.len()
            processed_df['word_count'] = processed_df['content'].str.split().str.len()
            
            # Save processed data
            processed_path = os.path.join(PROCESSED_DIR, f"{filename}_processed.csv")
            processed_df.to_csv(processed_path, index=False)
            logger.info(f"✅ Processed data saved to: {processed_path}")
        
        return raw_path
    
    def print_stats(self):
        """Print fetching statistics."""
        logger.info("=== FETCH STATISTICS ===")
        logger.info(f"Total reviews fetched: {self.stats['fetched']}")
        logger.info(f"Security-related reviews: {self.stats['security_related']}")
        logger.info(f"Errors encountered: {self.stats['errors']}")
        
        if self.stats['fetched'] > 0:
            security_pct = (self.stats['security_related'] / self.stats['fetched']) * 100
            logger.info(f"Security relevance: {security_pct:.1f}%")


def validate_app_id(platform: str, app_id: str) -> bool:
    """Validate app ID format for the given platform."""
    if platform == 'google':
        return '.' in app_id and len(app_id.split('.')) >= 2
    elif platform == 'apple':
        return app_id.isdigit() and len(app_id) >= 6
    return False


def main():
    """Main function with enhanced argument parsing and validation."""
    parser = argparse.ArgumentParser(
        description="Fetch app reviews for consumer security analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch Google Play reviews
  python fetch_reviews.py --platform google --app_id com.wsandroid.suite --max_reviews 1000
  
  # Fetch Apple App Store reviews
  python fetch_reviews.py --platform apple --app_id 724596345 --country us --max_reviews 500
        """
    )
    
    # Required arguments
    parser.add_argument('--platform', 
                       choices=['google', 'apple'], 
                       required=True,
                       help='Platform to fetch reviews from')
    
    parser.add_argument('--app_id', 
                       required=True,
                       help='App ID (package name for Google, numeric ID for Apple)')
    
    # Optional arguments
    parser.add_argument('--country', 
                       default='us',
                       help='Country code (default: us)')
    
    parser.add_argument('--max_reviews', 
                       type=int, 
                       default=1000,
                       help='Maximum number of reviews to fetch (default: 1000)')
    
    parser.add_argument('--output', 
                       help='Custom output filename (without extension)')
    
    parser.add_argument('--delay', 
                       type=float, 
                       default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    
    parser.add_argument('--lang', 
                       default='en',
                       help='Language code for Google Play (default: en)')
    
    parser.add_argument('--verbose', 
                       action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate app ID
    if not validate_app_id(args.platform, args.app_id):
        logger.error(f"Invalid app ID '{args.app_id}' for platform '{args.platform}'")
        sys.exit(1)
    
    # Initialize fetcher
    fetcher = ReviewFetcher(delay=args.delay)
    
    try:
        # Fetch reviews
        if args.platform == 'google':
            df = fetcher.fetch_google_reviews(
                app_id=args.app_id,
                lang=args.lang,
                country=args.country,
                max_reviews=args.max_reviews
            )
        else:  # apple
            df = fetcher.fetch_apple_reviews(
                app_id=args.app_id,
                country=args.country,
                max_reviews=args.max_reviews
            )
        
        if df.empty:
            logger.error("No reviews were fetched. Exiting.")
            sys.exit(1)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.output:
            filename = args.output
        else:
            filename = f"{args.platform}_{args.app_id}_{timestamp}"
        
        # Save data
        saved_path = fetcher.save_reviews(df, filename)
        
        # Print statistics
        fetcher.print_stats()
        
        logger.info("=== SUMMARY ===")
        logger.info(f"✅ Successfully fetched {len(df)} reviews")
        logger.info(f"📁 Data saved to: {saved_path}")
        logger.info("🎉 Fetch completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
