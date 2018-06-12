import httplib2
import json
import random
import requests
import string

from flask import (
    flash,
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session as login_session,
    url_for,
)
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from models import (
    add_item,
    add_user,
    connect_to_db,
    Base,
    Category,
    delete_item,
    get_category,
    get_category_items,
    get_item,
    get_user_id,
    Item,
    User,
)

app = Flask(__name__)


CLIENT_PATH = '../client_secrets.json'
CLIENT_ID = json.loads(open(CLIENT_PATH, 'r').read())['web']['client_id']


def is_logged_in():
    return 'user_id' in login_session

def is_authorized(user_id):
    return 'user_id' in login_session and login_session['user_id'] == user_id

def clear_login_session():
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['user_id']
    del login_session['state']


@app.route('/login')
def showLogin():
    # Create CSRF token to pass in with login request
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(CLIENT_PATH, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = get_user_id(data["email"])
    if not user_id:
        user = add_user(login_session['username'], login_session['email'])
        user_id = user.id
    login_session['user_id'] = user_id

    output = 'You are logged in as '
    output += login_session['username']
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token', None)
    if access_token is None:
        response = make_response(json.dumps('User not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        clear_login_session()
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('getCatalog'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/', defaults={'json': None})
@app.route('/<json>')
def getCatalog(json):
    # Get a list of all categories for display in sidebar
    categories = get_category(category_id=None)
    # Shows all items in descending order of creation date
    items = get_category_items(category_id=None)

    if json == '.json':
        return jsonify(Categories=[category.serialize for category in categories])

    return render_template(
        'index.html',
        categories=categories,
        items=items
    )


@app.route('/<int:category_id>')
@app.route('/<int:category_id><json>')
def getCategory(category_id=None, json=None):

    # Get a list of all categories for display in sidebar
    categories = get_category(category_id=None)
    # Shows all items for selected category alphabeticcally
    items = get_category_items(category_id)

    if json == '.json':
        return jsonify(Categories=[category.serialize
                                   for category in categories
                                   if category.id == category_id ])

    return render_template(
        'index.html',
        categories=categories,
        items=items,
        category_id=items[0].category_id,
        category_name=items[0].category.name
    )


@app.route('/<int:category_id>/<int:item_id>')
@app.route('/<int:category_id>/<int:item_id><json>')
def getCategoryItem(category_id=None, item_id=None, json=None):

    # Get a list of all categories for display in sidebar
    categories = get_category(category_id=None)

    # Shows items for selected category
    items = get_category_items(category_id)

    if json == '.json':
        return jsonify(Item=[item.serialize
                                   for item in items
                                   if item.id == item_id ])
    return render_template(
        'index.html',
        categories=categories,
        items=items,
        category_id=items[0].category_id,
        category_name=items[0].category.name,
        item_id=item_id
    )


@app.route('/item/add', methods=['GET', 'POST'])
def addItem():
    if not is_logged_in():
        flash("You must be logged in to perform that action.")
        return redirect(url_for('getCatalog'))

    if request.method == 'POST':
        item = add_item(
            name=request.form['name'],
            description=request.form['description'],
            url=request.form['url'],
            category_id=request.form['category_id']
        )
        return redirect(url_for(
            'getCategoryItem',
            category_id=item.category_id,
            item_id=item.id)
        )
    else:
        categories = get_category(category_id=None)
        return render_template(
            'add.html',
            categories=categories,
        )


@app.route('/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_id=None, item_id=None):
    if not is_logged_in():
        flash("You must be logged in to perform that action.")
        return redirect(url_for('getCatalog'))

    item = get_item(item_id)
    if not is_authorized(item.user_id):
        flash("You may only edit items you have created.")
        return redirect(url_for('getCategory', category_id=category_id))

    if request.method == 'POST':
        item.update_item(
            name=request.form['name'],
            description=request.form['description'],
            url=request.form['url'],
            category_id=request.form['category_id']
        )
        return redirect(url_for(
            'getCategoryItem',
            category_id=item.category_id,
            item_id=item.id)
        )
    else:
        categories = get_category(category_id=None)
        if item:
            return render_template(
                'edit.html',
                categories=categories,
                item=item,
            )


@app.route('/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(category_id=None, item_id=None):
    if not is_logged_in():
        flash("You must be logged in to perform that action.")
        return redirect(url_for('getCatalog'))

    item = get_item(item_id)
    if not is_authorized(item.user_id):
        flash("You may only delete items you have created.")
        return redirect(url_for('getCategory', category_id=category_id))

    if request.method == 'POST' and item_id:
        delete_item(item_id)
        return redirect(url_for('getCategory', category_id=category_id))
    else:
        item = get_item(item_id)
        return render_template(
            'delete.html',
            category_id=item.category_id,
            item=item
        )


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000, debug=True)
