import os
import re
import json
import asyncio
from pathlib import Path
import pandas as pd
from typing import List
#from get_page_source_local import get_page_source_local
#from get_urls import get_urls, get_body
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import requests
from xml.etree import ElementTree

cwd = os.getcwd()
path = Path(cwd).parent.absolute()


async def crawl_sequential(urls: List[str], names:List[str]):
    print("\n=== Sequential Crawling with Session Reuse ===")

    browser_config = BrowserConfig(
        user_agent_mode="random",
        text_mode=True,
        headless=True,
        # For better performance in Docker or low-memory environments:
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(),
        verbose=True
    )

    # Create the crawler (opens the browser)
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1"  # Reuse the same session across all URLs
        for url,name in urls, names:
            result = await crawler.arun(
                url=url,
                config=crawl_config,
                session_id=session_id
            )
            if result.success:
                print(f"Successfully crawled: {url}")
                # E.g. check markdown length
                print(f"Markdown length: {len(result.markdown_v2.raw_markdown)}")
                # Save to txt
                fname = name.replace(" ", "_").replace("-", "_")
                with open(f"{path}/outputs/{fname}.txt", "w") as txt_file:
                    txt_file.write(result.cleaned_html)
                # Save markdown
                with open(f"{path}/outputs/{fname}.md", "w") as md_file:
                    md_file.write(result.raw_markdown)
            else:
                print(f"Failed: {url} - Error: {result.error_message}")
    finally:
        # After all URLs are done, close the crawler (and the browser)
        await crawler.close()



async def main():
    urls = ['https://www.aircanada.com/ca/en/aco/home/plan/check-in-information.html',
            'https://www.aircanada.com/ca/en/aco/home/plan/travel-requirements.html']
    names = ['Check-In Information', 'Travel Requirements']
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_sequential(urls,names)
    else:
        print("No URLs found to crawl")

if __name__ == "__main__":
    asyncio.run(main())