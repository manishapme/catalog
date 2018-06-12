from models import (
    add_category,
    add_item,
    add_user,
    delete_category,
    delete_item,
    delete_user,
    get_category,
    get_user_id,
)


ADMIN_EMAIL = 'adminemail'


def populate_users():
    """Create minimum sample data for the user table."""

    users = [{
        'username': 'mary',
        'email': 'mary @ example.com'}, {
        'username': 'john',
        'email': 'john @ example.com'}, {
        'username': 'M P',
        'email': ADMIN_EMAIL
    }]
    for user in users:
        add_user(username=user['username'], email=user['email'])


def populate_categories():
    """Create minimum sample data for the category table."""

    user_id = get_user_id(ADMIN_EMAIL)
    categories = [{'name': 'Movie', 'user_id': user_id}, {
                   'name': 'Book', 'user_id': user_id}, {
                   'name': 'Music', 'user_id': user_id}, {
                   'name': 'Exhibition', 'user_id': user_id}]
    for category in categories:
        print category['user_id']
        add_category(name=category['name'], user_id=category['user_id'])


def populate_items():
    """Create minimum sample data for the item table."""

    user_id = get_user_id(ADMIN_EMAIL)
    categories = get_category(category_id=None)
    items = [{'name': '1name',
              'description': '1description',
              'url': '1url',
              'category_id': categories[0].id,
              'user_id': user_id}, {
              'name': '1name1',
              'description': '1description1',
              'url': '1url1',
              'category_id': categories[0].id,
              'user_id': user_id}, {
              'name': '2name',
              'description': '2description',
              'url': '2url',
              'category_id': categories[1].id,
              'user_id': user_id}, {
              'name': '2name1',
              'description': '2description1',
              'url': '2url1',
              'category_id': categories[1].id,
              'user_id': user_id}, {
              'name': '3name',
              'description': '3description',
              'url': '3url',
              'category_id': categories[2].id,
              'user_id': user_id}, {
              'name': '3name1',
              'description': '3description1',
              'url': '3url1',
              'category_id': categories[2].id,
              'user_id': user_id}, {
              'name': '4name',
              'description': '4description',
              'url': '4url',
              'category_id': categories[3].id,
              'user_id': user_id}, {
              'name': '4name1',
              'description': '4description1',
              'url': '4url1',
              'category_id': categories[3].id,
              'user_id': user_id
              }]
    for item in items:
        add_item(
            name=item['name'],
            description=item['description'],
            url=item['url'],
            category_id=item['category_id'],
            user_id=item['user_id']
        )


if __name__ == '__main__':
    # always clean slate test data
    delete_user(user_id=None)
    delete_item(item_id=None)
    delete_category(category_id=None)

    print 'populate_users'
    populate_users()
    print 'populate_categories'
    populate_categories()
    print 'populate_items'
    populate_items()
