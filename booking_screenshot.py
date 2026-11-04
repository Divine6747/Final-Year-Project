
from pathlib import Path
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


def handle_cookie_banner(page):
    """Attempt to dismiss the cookie consent banner."""
    decline_button = page.get_by_role(
        "button", name="Decline", exact=True
    )

    try:
        decline_button.first.click(timeout=2000)
        print("Cookie banner dismissed.")
        page.wait_for_timeout(1000)
    except PlaywrightTimeoutError:
        print("Cookie banner not found or already dismissed.")


def inspect_and_close_dialogs(page):
    """Close the Booking.com sign-in discount card."""
    dialog = page.get_by_role(
        "dialog",
        name=(
            "Window offering discounts of 10% or more "
            "when you sign in to Booking.com"
        )
    )

    try:
        if dialog.is_visible():
            close_button = dialog.get_by_role(
                "button",
                name="Dismiss sign in information.",
                exact=True
            )

            close_button.click(timeout=2000)
            page.wait_for_timeout(1000)
            print("Sign-in discount card dismissed.")
        else:
            print("Sign-in discount card not present.")

    except PlaywrightTimeoutError:
        print("Sign-in card or its close button was not found.")


def scroll_through_results(page, max_scrolls=10):
    "Scrolling through the results and monitor hotel listings."
    previous_count = 0
    unchanged_attempts = 0

    for step in range(max_scrolls):
        hotel_cards = page.get_by_test_id("property-card")
        current_count = hotel_cards.count()

        print(
            f"Scroll {step + 1}: "
            f"{current_count} hotel cards found."
        )

        if current_count <= previous_count:
            unchanged_attempts += 1
        else:
            unchanged_attempts = 0

        if unchanged_attempts >= 3:
            print("No additional hotel cards detected.")
            break

        previous_count = current_count

        # Scroll down gradually
        page.evaluate(
            "() => window.scrollBy(0, window.innerHeight * 0.7)"
        )

        # Allow the page to update
        page.wait_for_timeout(2000)

    print("Finished scrolling through results.")


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)

    page = browser.new_page(
        viewport={"width": 1280, "height": 720}
    )

    # Step 1: Open Booking.com
    page.goto("https://www.booking.com")
    page.wait_for_timeout(5000)

    # Step 2: Handle cookie consent
    handle_cookie_banner(page)

    # Step 3: Close the sign-in discount card
    inspect_and_close_dialogs(page)

    # Step 4: Enter and select the destination
    destination = page.get_by_placeholder(
        "Where are you going?",
        exact=True
    )

    destination.wait_for(state="visible", timeout=10000)
    destination.fill("Dublin")
    page.wait_for_timeout(2000)

    suggestions = page.get_by_role("option")

    print("\n*** Destination suggestions ***")

    for i in range(suggestions.count()):
        suggestion = suggestions.nth(i)

        if suggestion.is_visible():
            print(f"{i + 1}. {suggestion.inner_text()}")

    suggestions.filter(
        has_text="Dublin County, Ireland"
    ).first.click(timeout=5000)

    page.wait_for_timeout(1000)
    print("Destination selected.")

    # Step 5: Open the date picker
    date_button = page.get_by_test_id(
        "searchbox-dates-container"
    )

    if date_button.get_attribute("aria-expanded") != "true":
        date_button.click()

    calendar = page.get_by_test_id(
        "searchbox-datepicker-calendar"
    )

    calendar.wait_for(state="visible", timeout=10000)

    # Step 6: Select check-in and check-out dates
    check_in = calendar.locator(
        '[data-date="2026-11-15"]'
    )

    check_out = calendar.locator(
        '[data-date="2026-11-18"]'
    )

    check_in.wait_for(state="attached", timeout=10000)
    check_in.click(timeout=5000)

    page.wait_for_timeout(500)

    check_out.wait_for(state="attached", timeout=10000)
    check_out.click(timeout=5000)

    page.wait_for_timeout(1000)

    print("Check-in selected: 15 November 2026")
    print("Check-out selected: 18 November 2026")
    print("Date display:", date_button.inner_text())

    # Step 7: Confirm occupancy settings
    occupancy_button = page.get_by_test_id(
        "occupancy-config"
    )

    occupancy_button.click()
    page.wait_for_timeout(1000)

    done_button = page.get_by_role(
        "button",
        name="Done",
        exact=True
    )

    done_button.wait_for(state="visible", timeout=5000)
    done_button.click()

    page.wait_for_timeout(1000)

    print(
        "Occupancy confirmed: "
        "2 adults, 0 children, 1 room."
    )

    # Step 8: Save a screenshot of the completed search form
    project_folder = Path(__file__).resolve().parent

    form_screenshot = (
        project_folder / "booking_search_form.png"
    )

    page.screenshot(path=str(form_screenshot))

    print(f"Search form screenshot saved to: {form_screenshot}")

    # Step 9: Submit the search
    search_button = page.get_by_role(
        "button",
        name="Search",
        exact=True
    )

    search_button.click()

    page.wait_for_load_state(
        "domcontentloaded",
        timeout=30000
    )

    page.wait_for_timeout(5000)

    print("\n*** Search results ***")
    print("Current URL:", page.url)
    print("Page title:", page.title())

    # Step 10: Scroll through hotel results
    scroll_through_results(page, max_scrolls=10)

    # Step 11: Save a screenshot after scrolling
    results_screenshot = (
        project_folder / "booking_results.png"
    )

    page.screenshot(path=str(results_screenshot))

    print(f"Results screenshot saved to: {results_screenshot}")

    # Step 12: Keep the browser open briefly, then close
    page.wait_for_timeout(5000)
    browser.close()
