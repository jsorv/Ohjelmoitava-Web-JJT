# API Deployment

This follows the tutorial from the Programmable Web Project course. [Link](https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/exercise-3-api-documentation-and-hypermedia/).

Everything here is based on the tutorial mentioned above.

## Dependencies

- python3.12-venv

- supervisor

## Deployment instructions

First setup the environment you want to use. (Preferrably a virtual machine running on Linux, since isntructions are for a debian based system)

### Prepare project

1. First create a user for the system

``` sudo useradd --system weatherradar```

2. Add current user to the weatherrdar group

``` sudo usermod -aG weatherradar $USER ```

3. Log out and back in to make the group update

4. Create weatherradar directory and remove privileges from other users

``` sudo mkdir /opt/weatherradar ```

``` sudo chown weatherradar:weatherradar /opt/weatherradar ```

``` sudo chmod -R o-rwx /opt/weatherradar ```

5. Make sure python venv is installed

``` sudo apt update ```

``` sudo apt install python3.12-venv ```

After this most things are performed as the weatherradar user

6. Create venv 

``` sudo -u weatherradar python3 -m venv /opt/weatherradar/venv ```

7. Clone the repo to the weatherradar directory

``` git clone https://github.com/jsorv/Ohjelmoitava-Web-JJT.git /opt/weatherradar/weatherradar ```

8. Create the postactivate file with your preferred text editor and change the file permissions to owner only (except read for group for the next step)

``` sudo -u weatherradar (nano/vi/gedit) /opt/weatherradar/venv/bin/postactivate ```

``` sudo chmod 640 /opt/weatherradar/venv/bin/postactivate ```

Add the line ``` export GUNICORN_WORKERS=3 ```

9. Activate the venv and add the postactivate variables for your current user 

``` source /opt/weatherradar/venv/bin/activate ```
``` source /opt/weatherradar/venv/bin/postactivate ```
 
10. Go to the project directory and install dependencies

``` cd /opt/weatherradar/weatherradar ```

``` sudo -u weatherradar -E env PATH=$PATH python -m pip install -E API```

11. Set up database 

``` sudo -u weatherradar -E env PATH=$PATH python -m "API.scripts.populate_db" ```

### Enable supervisor

1. Create startup script for supervisor to use

```sudo -u weatherradar mkdir /opt/weatherradar/venv/scripts```

```sudo -u weatherradar (nano/vi/gedit) /opt/weatherradar/venv/scripts/start_gunicorn.sh```

```sudo chmod u+x /opt/weatherradar/venv/scripts/start_gunicorn.sh```

The script is found from [here](start_gunicorn.sh).

2. Install supervisor

``` sudo apt install supervisor ```

3. Create a supervisor .conf file for the application

```sudo (nano/vi/gedit) /etc/supervisor/conf.d/weatherradar.conf```

Conf file found from [here](weatherradar.conf)
 
4.  Create the log folder

``` sudo -u weatherradar mkdir /opt/weatherradar/logs ```

5. Reload supervisor

``` sudo systemctl reload supervisor ```

### NGINX it

1. Create an nginx file for weatherradar

```sudo (nano/vi/gedit) /etc/nginx/sites-available/weatherradar```

Found [here](./weatherradar)

(When deploying, change the server_name from localhost to the domain name or ip you are serving)

2. Make sure this is used

```sudo ln -s /etc/nginx/sites-available/weatherradar /etc/nginx/sites-enabled/weatherradar```

```sudo rm /etc/nginx/sites-enabled/default```

```sudo systemctl reload nginx```

### ngrok it (if that is your choice)

1. Make an ngrok account

2. From Welcome page choose linux and the Apt tab.

3. Follow the instructions

- Installing ngrok to the deployment machine

- Adding your authtoken

- Test it if you want (Gives you your own dev domain name that needs to replace localhost in the nginx file) 

ps. You might need to increase ```server_names_hash_bucket_size``` in /etc/nginx/nginx.conf for nginx to accept the abnormally long domain name from ngrok

4. Add ngrok to supervisor

``` sudo (nano/vi/gedit) /etc/supervisor/conf.d/ngrok.conf ```

Found [here](./ngrok.conf)

Add your user to be the user to make the ngrok auth token work

``` sudo supervisorctl reread ```

``` sudo supervisorctl update ```

``` sudo supervisorctl restart ngrok ```
