
echo "stopping nginx and killing all gunicorn "
sudo systemctl stop nginx
sudo killall gunicorn

echo "conferming gunicorn & nginx are down"
ps aux | grep gunicorn
systemctl status nginx

echo "starting nginx"
sudo systemctl start nginx
sudo nginx -s reload

echo "starting gunicorn"
#gunicorn -w 3 API:app > /dev/null 2>&1 &
gunicorn -w 3 API:app 
#gunicorn --workers 3 --bind 0.0.0.0:5000 API:app

echo "listing jobs"

