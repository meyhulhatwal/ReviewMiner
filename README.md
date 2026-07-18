# ReviewMiner
Automated web scraping project that extracts LG customer reviews from MouthShut using Selenium, performs sentiment analysis with TextBlob, and exports structured review data for analysis.
# LG Service Reviews Scraper with Sentiment Analysis

A Python-based web scraping project that extracts customer reviews of **LG Service India** from MouthShut.com using Selenium. The scraped reviews are automatically analyzed using TextBlob to determine customer sentiment and exported into CSV and Excel formats.

---

## Features

- Scrapes multiple review pages automatically
- Extracts:
  - Review Title
  - Rating
  - Review Date
  - Review Content
- Performs Sentiment Analysis using TextBlob
- Calculates polarity score
- Saves results as CSV
- Displays sentiment summary after scraping

---

## Project Structure

```
LG-MouthShut-Review-Scraper
│
├── data
│   ├── raw
│   └── processed
│
├── screenshots
│
├── src
│   └── scraper.py
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Technologies Used

- Python
- Selenium
- Pandas
- TextBlob
- WebDriver Manager

---

## Workflow

1. Launch Chrome Driver
2. Visit MouthShut review pages
3. Extract review details
4. Clean review data
5. Perform sentiment analysis
6. Store data into CSV
7. Display summary statistics

---

## Dataset Columns

| Column | Description |
|---------|-------------|
| Subject | Review Title |
| Rating | Customer Rating |
| Date | Review Date |
| Content | Review Text |
| Sentiment | Positive / Neutral / Negative |
| Sentiment Score | TextBlob Polarity Score |

---

## Sample Output

| Subject | Rating | Sentiment |
|----------|--------|-----------|
| Excellent Service | 5 | Positive |
| Worst Experience | 1 | Negative |
| Average Service | 3 | Neutral |

---

## How to Run

Clone the repository

```bash
git clone https://github.com/yourusername/LG-MouthShut-Review-Scraper.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python src/scraper.py
```

---

## Sentiment Classification

| Polarity | Sentiment |
|-----------|-----------|
| > 0.1 | Positive |
| -0.1 to 0.1 | Neutral |
| < -0.1 | Negative |

---

## Future Improvements

- Export directly to Excel
- Interactive Dashboard
- Streamlit Web App
- Word Cloud Visualization
- Charts using Matplotlib
- Support multiple product pages

---

## Author

**Your Name**

B.Tech Computer Science (AI & ML)
