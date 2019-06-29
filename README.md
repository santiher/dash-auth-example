# Dash authentication and access management

In this repository there are two example python
[Dash](https://dash.plot.ly/getting-started) dashboards with authentication and
access management.

Authentication is done by receiving an http authentication header with the
username and password. Upon successful authentication, an encrypted json web
token cookie is returned to the user and used in subsequent request to validate
the user.

## Authentication only

The authentication only example in the `auth_only` directory only checks that
the user is allowed to see the dashboard and shows *all* the dashboard.

The authentication is done by another service (not the dash app), which is
requested by an nginx reverse proxy before forwarding the request to the dash
app. The dash app is only requested if the authentication service gave the ok.

This is done using Nginx's [auth request module](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-subrequest-authentication/).

## Authentication and access management

The authentication and access management example in the `auth_iam` directory
authenticates the user and only provides access to the allowed sections of the
dashboard using a multi-page app.

The json web token cookie from the user is assumed to have an
`allowed_resources` item with a list of allowed pages. If the special page
`_all_` is contained, the user is allowed full access to the dashboard.

## Users

Two users are created on the examples:

| username | password | pages     |
| -------- | -------- | --------- |
| mica     | 1234     | all       |
| mike     | 123456   | marketing |

The users themselves are hardcoded, this example is not intended to be a users
and passwords example.

## Architecture

An [Nginx](https://www.nginx.com/) serves requests before they get to the dash
app.
The Nginx reverse proxy can force https between itself and the outside world,
so you can have it secured there, but keep http between nginx and the
dashboard.
The flow goes like:

1. Nginx receives a request for one of the dashboard's resource.
2. Nginx forwards the authentication service to authenticate the user.
3. The authentication service might deny access or allow it and return cookies
   for the user (containing an encrypted payload with data about the user like
   username, allowed resources, whatever).  
   At this point the request should already have cookies or an authentication
   header.
4. Nginx returns an access denied if it corresponds or forwards the request to
   the dashboard (containing the cookies).
5. The dashboard replies to Nginx, which replies to the user.

Following this architecture, in order to add authentication to a Dash app, you
don't have to modify your dashboard at all.

In order to add access management and restrict the sections of the dashboard a
user can see, the dash app has to be modified.

Take into account that the authentication service endpoints and the dash app
can be the same.

```
        ^
~~~~~~~ | ~~~~~~~  outside world
        |
+---------------+      +------------------------+
|     nginx     + <--- | authentication service |
+-------+-------+      +------------------------+
       ^ |          v
       | |      Request with authentication service. Deny or allow with cookies
       | |
 Reply | | Request with authenticated users with cookies
       | v
  +---------------+
+---------------+ |
|    gunicorn   +-+
+-------+-------+
        ^
        |
        v
  +---------------+
+---------------+ |
|  dash (flask) +-+
+-------+-------+
```

## Access management

In order to perform access management, a few changes / conventions have to be
done in Dash.

### Cookies and json web tokens

Once the user has been authenticated, a JSON web token cookie named
*example_jwt* is returned. This cookie is used in subsequent requests to
authenticate the user and get its allowed resources.

The token is encripted using the *secret* variable.

### Sections

We will divide the dashboard in sections (different tabs in a multi-page app),
this would work to have for instance, a section for each business unit or
manager. E.g.: one for marketing, one for human resources, etc.

In order to handle access management, dash components' ids have to be prefixed
with {section_name}- (e.g.: marketing-plot for the plot in the marketing
section).

### Allowed sections

We will add an `allowed_resources` key in the user cookie with an array of
allowed sections.

If the special keyword `_all_` is included, the user will be available to see
all sections. E.g.:

* `['marking']`: grants access to the marketing tab.
* `['marketing', 'hr']`: grants access to the marketing and hr tabs.
* `['_all_']`: grants access to all the tabs.

## Docker

In order to run the examples using [docker](https://www.docker.com/) you need
docker and docker-compose installed.

Running the exapmle servers with docker from the docker directories:

* Build: `docker-compose build`
* Start: `docker-compose up`

The examples will run a minimal dash dashboard with authentication that can be
accessed in the localhost 80 or 443 ports ([here](http://127.0.0.1)), as the
nginx redirects http to https with a self signed certificate, you will be asked
to trust the server.
