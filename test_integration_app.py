import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
import pytest

# Integration test suite exercising key flows across the app using Flask test client.


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'testkey'
    return app.test_client()


def set_session_username(client, username: str):
    """Helper to set the session's username for authenticated flows."""
    with client.session_transaction() as sess:
        sess['username'] = username


# ------------------ Public pages and redirects ------------------

def test_home_page_accessible(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_sign_in_and_sign_up_pages_accessible(client):
    assert client.get('/sign-in').status_code == 200
    assert client.get('/sign-up').status_code == 200
    assert client.get('/forgot-password').status_code == 200


def test_protected_pages_redirect_when_anonymous(client):
    # purchase and update-payment should redirect to sign-in when not logged in
    r1 = client.get('/purchase', follow_redirects=False)
    r2 = client.get('/update-payment', follow_redirects=False)
    assert r1.status_code in (301, 302)
    assert r2.status_code in (301, 302)
    loc1 = r1.headers.get('Location', '')
    loc2 = r2.headers.get('Location', '')
    assert loc1.endswith('sign-in') or '/sign-in' in loc1
    assert loc2.endswith('sign-in') or '/sign-in' in loc2


# ------------------ Auth flow (session-based) ------------------

def test_session_login_allows_access_and_logout_revokes(client):
    # Simulate login by setting session username
    set_session_username(client, 'user1')

    # Now purchase and update-payment should be accessible
    assert client.get('/purchase').status_code == 200
    assert client.get('/update-payment').status_code == 200

    # Logout clears session and protected pages redirect again
    lr = client.get('/logout', follow_redirects=False)
    assert lr.status_code in (301, 302)

    r1 = client.get('/purchase', follow_redirects=False)
    r2 = client.get('/update-payment', follow_redirects=False)
    assert r1.status_code in (301, 302)
    assert r2.status_code in (301, 302)


# ------------------ Admin-guarded pages ------------------

def test_admin_pages_require_admin_user(client):
    # Non-admin user gets 'no permission' instead of 200; ensure no KeyError
    set_session_username(client, 'regular_user')

    # sales-report, vehicle-inventory, update-user are admin-only
    sr = client.get('/sales-report')
    vi = client.get('/vehicle-inventory')
    uu = client.get('/update-user')

    assert sr.status_code == 200 and b'no permission' in sr.data
    assert vi.status_code == 200 and b'no permission' in vi.data
    assert uu.status_code == 200 and b'no permission' in uu.data

    # Admin user should access these pages
    set_session_username(client, 'Admin')

    sr2 = client.get('/sales-report')
    vi2 = client.get('/vehicle-inventory')
    uu2 = client.get('/update-user')

    assert sr2.status_code == 200
    assert vi2.status_code == 200
    assert uu2.status_code == 200


# ------------------ JSON endpoints smoke tests ------------------

def test_get_data_endpoint_smoke(client):
    # Should return JSON and not 500 regardless of DB availability
    r = client.get('/get-data')
    assert r.status_code == 200
    # Content type includes json
    assert 'application/json' in r.headers.get('Content-Type', '').lower()


def test_get_order_data_endpoint_smoke(client):
    r = client.get('/get-order-data')
    assert r.status_code == 200
    assert 'application/json' in r.headers.get('Content-Type', '').lower()


def test_get_user_data_endpoint_smoke_authenticated(client):
    # GET branch uses session['username'] and returns JSON
    set_session_username(client, 'user1')
    r = client.get('/get-user-data')
    assert r.status_code == 200
    assert 'application/json' in r.headers.get('Content-Type', '').lower()


# ------------------ Page render sanity checks (authenticated) ------------------

def test_purchase_and_update_payment_render_when_logged_in(client):
    set_session_username(client, 'user1')

    rp = client.get('/purchase')
    ru = client.get('/update-payment')

    assert rp.status_code == 200
    assert ru.status_code == 200

    html_p = rp.data.decode('utf-8', errors='ignore')
    html_u = ru.data.decode('utf-8', errors='ignore')

    assert 'Purchase' in html_p
    assert 'Payment' in html_u or 'Mail' in html_u


# ------------------ Sign-up and Sign-in POST smoke (no DB required) ------------------

def test_sign_up_and_sign_in_smoke(client):
    # Avoid coupling with DB; assert that endpoints accept POST without 500
    signup = client.post('/sign-up', data={
        'first-name': 'Int',
        'last-name': 'Test',
        'username': 'int_test_user',
        'email': 'int_test@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert signup.status_code in (200, 302)

    signin = client.post('/sign-in', data={
        'username': 'int_test_user',
        'password': 'Password123!'
    }, follow_redirects=True)
    # Could redirect to home on success or re-render sign-in on failure (no DB)
    assert signin.status_code in (200, 302)
