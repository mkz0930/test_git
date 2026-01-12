import argparse
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

PRICE_SELECTORS = [
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    "#priceblock_saleprice",
    "#priceblock_pospromoprice",
    "#priceblock_businessprice",
    "span.a-price span.a-offscreen",
    "span.a-price-whole",
]


def extract_price(page) -> str | None:
    for selector in PRICE_SELECTORS:
        locator = page.locator(selector).first
        if locator.count() == 0:
            continue
        try:
            if not locator.is_visible():
                continue
            text = locator.inner_text().strip()
        except PlaywrightTimeoutError:
            continue
        if text:
            return text
    return None


def fetch_price(url: str, timeout_ms: int = 30000) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            page.wait_for_load_state("networkidle", timeout=timeout_ms)
        except PlaywrightTimeoutError:
            pass
        price = extract_price(page)
        browser.close()

    if not price:
        raise RuntimeError("未找到价格，请检查链接或页面结构是否变化。")
    return price


def main() -> None:
    parser = argparse.ArgumentParser(
        description="使用 Playwright 抓取亚马逊商品价格",
    )
    parser.add_argument("url", help="亚马逊商品详情页 URL")
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=30000,
        help="页面加载超时时间（毫秒）",
    )
    args = parser.parse_args()

    price = fetch_price(args.url, timeout_ms=args.timeout_ms)
    print(price)


if __name__ == "__main__":
    main()
