import os
from flask import Flask, redirect, url_for, session, render_template, jsonify, request
from auth import init_oauth, oauth
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize auth
init_oauth(app)

# In-memory storage for demo
campaigns = [
    {
        'id': 'OP-001',
        'name': 'Target Recon - CorpNet',
        'status': 'Active',
        'targets': 47,
        'captured': 23,
        'created': '2026-06-28',
        'type': 'Google OAuth Phish'
    },
    {
        'id': 'OP-002',
        'name': 'VPN Cred Harvest',
        'status': 'Active',
        'targets': 128,
        'captured': 89,
        'created': '2026-07-01',
        'type': 'Credential Harvesting'
    }
]

@app.route('/')
def index():
    return render_template('index.html', logged_in='user' in session)

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.parse_id_token(token)
    session['user'] = {
        'name': userinfo.get('name', 'Unknown'),
        'email': userinfo.get('email', 'unknown@email.com'),
        'picture': userinfo.get('picture', '')
    }
    session['logged_in'] = True
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('index.html', logged_in=True, user=session['user'], campaigns=campaigns)

@app.route('/api/campaigns')
def api_campaigns():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(campaigns)

@app.route('/api/stats')
def api_stats():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'total_campaigns': len(campaigns),
        'active_campaigns': sum(1 for c in campaigns if c['status'] == 'Active'),
        'total_targets': sum(c['targets'] for c in campaigns),
        'total_captured': sum(c['captured'] for c in campaigns)
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
