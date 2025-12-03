# -Unit-Integration-_test
# Test Suite Overview

This repository includes unit and integration tests built with `pytest` for a Flask web application.

- Unit tests focus on page rendering and route behavior using the Flask test client.
- Integration tests exercise end-to-end flows across multiple pages and permissions.

Below are details of the available test suites.

---

## Unit Testing for `purchase` Page

This testing script verifies the functionality of the `/purchase` page and ensures the page works correctly and displays the expected content when a user is logged in.

### Setup

- The script adds the parent directory to `sys.path` so it can import the Flask app.
- The `pytest` framework is used for running the tests.

### Fixtures

1. `client`
   - Creates a test version of the Flask app.
   - Enables testing mode (`TESTING=True`) for accurate test behavior.
   - Sets a secret key for session handling.
   - Returns a Flask test client to simulate requests.

2. `logged_in_client`
   - Uses the `client` fixture.
   - Simulates a logged-in user by adding a fake `username` to the session.
   - Required because the `/purchase` page needs an authenticated user.

### Tests

1. `test_purchase_page_status_code`
   - Sends a GET request to `/purchase` with a logged-in client.
   - Expects a 200 OK status.

2. `test_purchase_page_contains_required_text`
   - Sends a GET request to `/purchase` with a logged-in client.
   - Verifies the page contains key sections: "Purchase", "VEHICLE NAME", "Mail Information", "Payment Information", "Delivery Options", and "Confirm Purchase".

---

## Unit Testing for `sign-in` Page

File: `Tests/test_sign_in.py`

### Tests
- `test_sign_in_page_status_code`: GET `/sign-in` returns 200.
- `test_sign_in_page_contains_required_text`: Page contains common username/password and submit elements.
- `test_update_payment_redirects_when_not_logged_in`: Anonymous access to `/update-payment` redirects to sign-in (supports relative or absolute redirect target).
- `test_sign_in_post_does_not_crash_without_db`: POST to `/sign-in` returns 200/302 (smoke, DB-agnostic).

---

## Unit Testing for `sign-up` Page

File: `Tests/test_sign_up.py`

### Tests
- `test_sign_up_page_status_code`: GET `/sign-up` returns 200.
- `test_sign_up_page_contains_required_text`: Page contains first/last name, username, email, password, and submit elements.
- `test_sign_up_post_does_not_crash_without_db`: POST to `/sign-up` returns 200/302 (smoke, DB-agnostic).

---

## Integration Tests

Folder: `integration tests/`

File: `integration tests/test_integration_app.py`

### Coverage
- Public pages accessible: `/`, `/sign-in`, `/sign-up`, `/forgot-password`.
- Protected pages redirect when anonymous: `/purchase`, `/update-payment`.
- Session-based auth flow: set session username → access protected pages → logout → redirects again.
- Admin-only pages: non-admin receives "no permission"; `Admin` user gets 200 for `/sales-report`, `/vehicle-inventory`, `/update-user`.
- JSON endpoints smoke: `/get-data`, `/get-order-data`, `/get-user-data` (authenticated).
- Auth endpoints POST smoke: `/sign-up` and `/sign-in` accept POST without 500.

---

## Running Tests

From the project root directory:

- Run all tests:
  - `pytest -q`

- Run only unit tests:
  - `pytest -q Tests`

- Run only integration tests:
  - `pytest -q "integration tests"`

