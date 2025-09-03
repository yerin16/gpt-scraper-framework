# 🕵️ GPT Scraper Framework

A modular framework for **scraping GPTs** from publicly available GPT stores and other online sources.  
This project was developed as part of a research project led by **PhD student Evin Jaff**, with contributions from collaborators including myself.

---

## 📌 Features
- Multiple scrapers targeting different GPT directories (e.g., `allgpts.co`, `botsbarn.com`, `plugin.surf`, etc.).
- Unified interface: every scraper implements a `scrape()` method returning a list of OpenAI GPT URLs.
- Selenium-based scraping for dynamic content handling.
- Utility functions for URL extraction, backups, logging, and optional email reporting.
- Easily extensible—new scrapers can be added with minimal setup.