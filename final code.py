from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from textblob import TextBlob
import random

def print_header():
    """Print formatted header"""
    print("=" * 70)
    print("🔍 MouthShut Reviews Scraper with Sentiment Analysis")
    print("=" * 70)

def print_page_progress(page, total_pages):
    """Print page progress in desired format"""
    print(f"Scraping page {page}...")

def print_completion_summary(df):
    """Print completion summary in desired format"""
    print(" ")
    print("📊 Sentiment Analysis Summary:")
    
    # Get sentiment counts
    sentiment_counts = df['Sentiment'].value_counts()
    print("Sentiment")
    
    # Print each sentiment with count
    for sentiment, count in sentiment_counts.items():
        print(f"{sentiment:<12}{count}")
    
    print("Name: count, dtype: int64")
    print(" ")
    
    # Calculate and print average polarity score
    avg_polarity = df['Sentiment_Score'].mean()
    print(f"Average Polarity Score: {avg_polarity:.3f}")
    print(" ")
    
    # Print completion message
    filename = 'lg_mouthshut_reviews_selenium_with_sentiment.csv'
    print(f"✅ Scraping completed! Data saved to {filename}")

def analyze_sentiment(text):
    """Analyze sentiment of the given text using TextBlob"""
    try:
        if not text or text == 'N/A' or not isinstance(text, str):
            return 'Neutral', 0.0
        
        # Create TextBlob object
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Classify sentiment based on polarity
        if polarity > 0.1:
            sentiment = 'Positive'
        elif polarity < -0.1:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        return sentiment, round(polarity, 3)
    
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return 'Neutral', 0.0

def format_date_to_standard(raw_date):
    """Convert date to DD/MM/YYYY format"""
    try:
        # Handle "X days ago" format
        if 'days ago' in raw_date.lower():
            days_match = re.search(r'(\d+)\s+days?\s+ago', raw_date)
            if days_match:
                days = int(days_match.group(1))
                target_date = datetime.now() - timedelta(days=days)
                return target_date.strftime('%d/%m/%Y %H:%M:%S')
        
        # Handle "X day ago" (singular)
        elif 'day ago' in raw_date.lower():
            target_date = datetime.now() - timedelta(days=1)
            return target_date.strftime('%d/%m/%Y %H:%M:%S')
        
        # Handle "X weeks ago"
        elif 'weeks ago' in raw_date.lower():
            weeks_match = re.search(r'(\d+)\s+weeks?\s+ago', raw_date)
            if weeks_match:
                weeks = int(weeks_match.group(1))
                target_date = datetime.now() - timedelta(weeks=weeks)
                return target_date.strftime('%d/%m/%Y %H:%M:%S')
        
        # Handle "X week ago" (singular)
        elif 'week ago' in raw_date.lower():
            target_date = datetime.now() - timedelta(weeks=1)
            return target_date.strftime('%d/%m/%Y %H:%M:%S')
        
        # Handle "X months ago"
        elif 'months ago' in raw_date.lower():
            months_match = re.search(r'(\d+)\s+months?\s+ago', raw_date)
            if months_match:
                months = int(months_match.group(1))
                target_date = datetime.now() - timedelta(days=months*30)  # Approximate
                return target_date.strftime('%d/%m/%Y %H:%M:%S')
        
        # Handle "X month ago" (singular)
        elif 'month ago' in raw_date.lower():
            target_date = datetime.now() - timedelta(days=30)
            return target_date.strftime('%d/%m/%Y %H:%M:%S')
        
        # Handle standard date formats like "12 Jan 2024"
        elif re.match(r'\d{1,2}\s+\w+\s+\d{4}', raw_date):
            parsed_date = datetime.strptime(raw_date, '%d %b %Y')
            return parsed_date.strftime('%d/%m/%Y %H:%M:%S')
        
        # If none of the above patterns match, return original
        else:
            return raw_date
            
    except Exception as e:
        print(f"Error parsing date '{raw_date}': {e}")
        return raw_date

def extract_subject(review_element):
    """Extract subject using multiple strategies"""
    selectors = [
        'strong a[id*="rptreviews_ctl"][id*="_lnkTitle"]',  # Primary pattern
        'a[id*="rptreviews_ctl"][id*="_lnkTitle"]',         # Without strong tag
        'a[id*="lnkTitle"]',                                # Simplified pattern
        'strong a[href*="/review/"]',                       # Alternative pattern
        'a[href*="/review/"]',                              # Fallback pattern
        'h2 a', 'h3 a', 'h4 a',                           # Header links
        '.review-title a', '.title a'                       # Class-based selectors
    ]
    
    for selector in selectors:
        try:
            subject_link = review_element.find_element(By.CSS_SELECTOR, selector)
            text = subject_link.text.strip()
            if text:
                return text
        except:
            continue
    
    return 'N/A'

def extract_rating(review_element):
    """Extract rating using multiple strategies"""
    try:
        # Primary pattern: count rated stars
        rated_stars = review_element.find_elements(By.CSS_SELECTOR, 'i.icon-rating.rated-star')
        if rated_stars:
            return len(rated_stars)
        
        # Alternative pattern: look for different star classes
        rated_stars = review_element.find_elements(By.CSS_SELECTOR, 'i.rated-star')
        if rated_stars:
            return len(rated_stars)
        
        # Another alternative: count stars with specific attributes
        all_stars = review_element.find_elements(By.CSS_SELECTOR, 'i[class*="rating"]')
        rated_count = 0
        for star in all_stars:
            if 'rated' in star.get_attribute('class'):
                rated_count += 1
        
        if rated_count > 0:
            return rated_count
        
        # Try looking for star ratings in different formats
        star_selectors = [
            '.star-rating .filled',
            '.rating-stars .active',
            '.stars .on',
            '[class*="star"][class*="fill"]'
        ]
        
        for selector in star_selectors:
            try:
                stars = review_element.find_elements(By.CSS_SELECTOR, selector)
                if stars:
                    return len(stars)
            except:
                continue
        
    except Exception as e:
        print(f"Error extracting rating: {e}")
    
    return 'N/A'

def extract_date(review_element):
    """Extract date using multiple strategies"""
    selectors = [
        'span[id*="rptreviews_ctl"][id*="_lblDateTime"]',  # Primary pattern
        'span[id*="lblDateTime"]',                         # Simplified pattern
        'span[class*="date"]',                             # Alternative pattern
        '.date',                                           # Fallback pattern
        '.review-date',                                    # Common class
        'time', '[datetime]',                              # Time elements
        '.timestamp', '.posted-date'                       # Additional patterns
    ]
    
    for selector in selectors:
        try:
            date_element = review_element.find_element(By.CSS_SELECTOR, selector)
            raw_date = date_element.text.strip()
            if raw_date:
                return format_date_to_standard(raw_date)
        except:
            continue
    
    return 'N/A'

def extract_content(review_element):
    """Extract content using multiple strategies"""
    try:
        # First, try to click "Read More" if it exists
        read_more_selectors = [
            'span.read-more',
            'a.read-more',
            'span[onclick*="readmore"]',
            '.read-more',
            '[onclick*="more"]',
            '.expand-text'
        ]
        
        for selector in read_more_selectors:
            try:
                read_more_buttons = review_element.find_elements(By.CSS_SELECTOR, selector)
                if read_more_buttons and read_more_buttons[0].is_displayed():
                    driver.execute_script("arguments[0].click();", read_more_buttons[0])
                    time.sleep(0.5)
                    break
            except:
                continue
        
        # Try different content selectors
        content_selectors = [
            'div.more.reviewdata',      # Primary pattern
            'div.reviewdata',           # Alternative pattern
            'div.more',                 # Simplified pattern
            '.review-content',          # Fallback pattern
            'div[class*="review"]',     # Generic pattern
            '.review-text',             # Common class
            '.content',                 # Simple content class
            'p'                         # Just paragraphs
        ]
        
        for selector in content_selectors:
            try:
                content_elements = review_element.find_elements(By.CSS_SELECTOR, selector)
                
                for content_div in content_elements:
                    # Try to get paragraphs first
                    paragraphs = content_div.find_elements(By.TAG_NAME, 'p')
                    if paragraphs:
                        content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
                        if content and len(content) > 10:  # Ensure meaningful content
                            return content
                    
                    # If no paragraphs, get direct text
                    text = content_div.text.strip()
                    if text and len(text) > 10:  # Ensure meaningful content
                        return text
                        
            except:
                continue
        
    except Exception as e:
        print(f"Error extracting content: {e}")
    
    return 'N/A'

def wait_for_page_load(driver, timeout=20):
    """Wait for page to load completely with multiple strategies"""
    try:
        # Wait for basic page structure
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # Try multiple selectors for review containers
        review_selectors = [
            (By.CLASS_NAME, 'review-article'),
            (By.CLASS_NAME, 'review'),
            (By.CSS_SELECTOR, '[class*="review"]'),
            (By.CSS_SELECTOR, 'article'),
            (By.CSS_SELECTOR, '.content')
        ]
        
        for selector_type, selector_value in review_selectors:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((selector_type, selector_value))
                )
                time.sleep(2)  # Additional wait for content to fully load
                return True
            except TimeoutException:
                continue
        
        return False
        
    except TimeoutException:
        return False

def get_review_elements(driver):
    """Get review elements using multiple strategies"""
    selectors = [
        'review-article',
        'review',
        'article',
        'content'
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CLASS_NAME, selector)
            if elements:
                return elements
        except:
            continue
    
    # Try CSS selectors
    css_selectors = [
        '[class*="review"]',
        'div[id*="review"]',
        'article',
        '.content > div'
    ]
    
    for selector in css_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return elements
        except:
            continue
    
    return []

def random_delay():
    """Add random delay to appear more human-like"""
    delay = random.uniform(2, 5)
    time.sleep(delay)

def setup_driver():
    """Setup Chrome driver with optimized options"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')  # Speed up loading
    options.add_argument('--disable-javascript')  # Disable JS if not needed
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Performance optimizations
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-backgrounding-occluded-windows')
    
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        return None

# Main execution starts here
print_header()

# Initialize the webdriver
driver = setup_driver()
if not driver:
    print("Failed to initialize webdriver. Exiting...")
    exit(1)

# Lists to store scraped data
subjects = []
ratings = []
dates = []
contents = []
sentiments = []
sentiment_scores = []

# Scrape all 11 pages
successful_pages = 0
failed_pages = []

for page in range(1, 12):
    print_page_progress(page, 11)
    
    url = f'https://www.mouthshut.com/product-reviews/lg-service-india-reviews-925891708-page-{page}.html'
    
    max_retries = 3
    retry_count = 0
    page_success = False
    
    while retry_count < max_retries and not page_success:
        try:
            # Navigate to the page
            driver.get(url)
            
            # Wait for page to load
            if not wait_for_page_load(driver):
                retry_count += 1
                random_delay()
                continue
            
            # Get all review blocks using multiple strategies
            review_blocks = get_review_elements(driver)
            
            if not review_blocks:
                retry_count += 1
                random_delay()
                continue
            
            page_reviews_processed = 0
            
            # Process each review
            for i, review in enumerate(review_blocks):
                try:
                    # Extract data using multiple strategies
                    subject = extract_subject(review)
                    rating = extract_rating(review)
                    date = extract_date(review)
                    content = extract_content(review)
                    
                    # Analyze sentiment
                    sentiment, sentiment_score = analyze_sentiment(content)
                    
                    # Add to lists
                    subjects.append(subject)
                    ratings.append(rating)
                    dates.append(date)
                    contents.append(content)
                    sentiments.append(sentiment)
                    sentiment_scores.append(sentiment_score)
                    
                    page_reviews_processed += 1
                    
                except Exception as e:
                    # Add N/A values to maintain consistency
                    subjects.append('N/A')
                    ratings.append('N/A')
                    dates.append('N/A')
                    contents.append('N/A')
                    sentiments.append('Neutral')
                    sentiment_scores.append(0.0)
            
            if page_reviews_processed > 0:
                successful_pages += 1
                page_success = True
            else:
                retry_count += 1
                random_delay()
                
        except WebDriverException as e:
            # Try to recover by reinitializing driver
            try:
                driver.quit()
                driver = setup_driver()
                if not driver:
                    break
            except:
                pass
            retry_count += 1
            random_delay()
            
        except Exception as e:
            retry_count += 1
            random_delay()
    
    if not page_success:
        failed_pages.append(page)
    
    # Add delay between pages to avoid being blocked
    random_delay()

# Close the browser
try:
    driver.quit()
except:
    pass

# Create DataFrame and save results
if subjects:  # Only create DataFrame if we have data
    df = pd.DataFrame({
        'Subject': subjects,
        'Rating': ratings,
        'Date': dates,  
        'Content': contents,
        'Sentiment': sentiments,
        'Sentiment_Score': sentiment_scores
    })

    # Save to CSV file with the exact filename format
    csv_filename = 'lg_mouthshut_reviews_selenium_with_sentiment.csv'
    df.to_csv(csv_filename, index=False)

    # Print completion summary in the desired format
    print_completion_summary(df)
else:
    print("No data was scraped. Please check the website structure and selectors.")