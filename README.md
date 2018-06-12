# Catalog

This is a small python application which will displays a list of categories and
shows items entered under each category. It provides basic CRUD access for the
logged in user and authenticates with Google OpenID.

## Getting Started

The system is pure python with a little bit of Bootstrap for front-end formatting.
A Vagrant file is provided from which you can access the application.

### Prerequisites

Have ability to bring up Vagrant machines on your local environment.

Have a Google ID which you can authenticate against.

Have a project and Google Credentials to authenticate against. 
See https://developers.google.com/youtube/analytics/registering_an_application

### Installing

Git clone repo or copy directory locally.

Navigate to correct directory `cd catalog` which contains the `Vagrantfile`.

In the `/catalog/catalog/seed_data.py` file, substitute your email for the `ADMIN_EMAIL` variable.

Replace the client_secrets.json file with your project's secrets file obtained from Google Developer Console.

Run Vagrantfile using `vagrant up`.

After successfully bringing up vagrant box, `vagrant ssh`.

On guest machine, `cd /vagrant/catalog`.

Populate the database with test data by running `python catalog/seed_data.py`.

### Running

To run simply execute ```python catalog/catalog.py``` in your console.

## Built With

Python

Jinja2

Bootstrap

Google Open ID / Oauth2

## Authors
* **Manisha Patel** - *Initial work* - [manishapme](https://github.com/manishapme)

## Acknowledgments
Extends https://github.com/udacity/ud330/tree/master/Lesson2/