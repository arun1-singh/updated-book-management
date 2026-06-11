# Flask + PostgreSQL Book Management Setup

This guide explains how to install PostgreSQL, create the database and
table, and configure it for a Flask CRUD application.

It works for **local development** and also includes **optional notes
for remote PostgreSQL setups**.

------------------------------------------------------------------------

# 1. Install PostgreSQL

``` bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

------------------------------------------------------------------------

# 2. Switch to the PostgreSQL System User

``` bash
sudo -i -u postgres
```

**Explanation:**\
This command switches from your Linux user to the **postgres Linux
user** which administers PostgreSQL.

------------------------------------------------------------------------

# 3. Open PostgreSQL CLI

``` bash
psql
```

**Explanation:**\
This starts the **PostgreSQL interactive terminal** where you can run
SQL commands.

------------------------------------------------------------------------

# 4. Set Password for PostgreSQL Superuser

``` sql
ALTER USER postgres WITH PASSWORD 'yourpassword';
```

**Explanation:**\
Sets a password for the **postgres database role**, which allows
applications like Flask to authenticate using a password.

------------------------------------------------------------------------

# 5. Create Application Database

``` sql
CREATE DATABASE demo_flask;
```

**Explanation:**\
Creates a new database that will store the tables used by the Flask
application.

------------------------------------------------------------------------

# 6. Connect to the Database

``` sql
\c demo_flask
```

**Explanation:**\
Switches the current session to the **demo_flask database** so tables
can be created inside it.

------------------------------------------------------------------------

# 7. Create Book Table

``` sql
CREATE TABLE book (
    id SERIAL PRIMARY KEY,         -- Auto-incrementing unique ID for each book
    publisher VARCHAR(255) NOT NULL, -- Name of the publisher
    name VARCHAR(255) NOT NULL,      -- Book title
    date DATE NOT NULL,              -- Publication date
    cost DECIMAL(10,2) NOT NULL      -- Book price
);
```

**Explanation:**\
Creates the main table used by the CRUD API.

------------------------------------------------------------------------

# 8. Flask Database Configuration

Example Flask configuration:

``` python
db_config = {
    "host": "localhost",
    "user": "postgres",
    "password": "yourpassword",
    "dbname": "demo_flask"
}
```

This configuration works with the **default PostgreSQL authentication
setup**.

------------------------------------------------------------------------

# 9. pg_hba.conf (Only Required for Remote Database Access)

For **local development**, the default configuration usually works.

Default file location:

    /etc/postgresql/16/main/pg_hba.conf

Default important entries:

    local   all             postgres                                peer
    local   all             all                                     peer
    host    all             all             127.0.0.1/32            scram-sha-256
    host    all             all             ::1/128                 scram-sha-256

Explanation:

  Type            Meaning
  --------------- ---------------------------------------
  peer            Linux user must match PostgreSQL role
  scram-sha-256   Password based authentication

------------------------------------------------------------------------

# 10. Remote PostgreSQL Setup (Optional)

If your Flask app connects from **another machine**, add this to
`pg_hba.conf`:

    host    all     all     0.0.0.0/0     scram-sha-256

Then restart PostgreSQL:

``` bash
sudo systemctl restart postgresql
```

Also update `postgresql.conf`:

    listen_addresses = '*'

⚠️ Only do this if you **need remote access**.

------------------------------------------------------------------------

# 11. Test Connection

``` bash
psql -U postgres -d demo_flask -h localhost
```

If it connects successfully, your setup is correct.

------------------------------------------------------------------------

# 12. Run Flask Application

``` bash
cd Server
source venv/bin/activate
python3 app.py
```

API will start at:

    http://localhost:5000

------------------------------------------------------------------------

# Summary

This setup provides:

-   PostgreSQL installation
-   Database creation
-   Table creation
-   Flask connection configuration
-   Optional remote database configuration

Works for both:

✔ Local development\
✔ Remote database deployments