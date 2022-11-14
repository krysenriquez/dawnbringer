## Setup

The first thing to do is to clone the repository:

```sh
$ cd <folder name>
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ pip install virtualenv
$ python -m venv <venv name>
$ source <venv_name>/Scripts/activate
```

Deactivate to exit virtualenv

```sh
$ deactivate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv`. This should
indicate the name of <venv name>

Once `pip` has finished downloading the dependencies:

```sh
(env)$ cd dawnbringer
(env)$ python manage.py makemigrations
(env)$ python manage.py migrate
(env)$ python manage.py runserver
```

After the creation of the migration scripts:

```sh
(env)$ python manage.py migrate
(env)$ python manage.py runserver
```

To run the Django Server:
```sh
(env)$ python manage.py runserver
```

And navigate to `http://127.0.0.1:8000/dawnbringer/admin`.
