
send_post(){
	curl -X POST -H "Content-Type: application/json" -d \
	'{"image" : "'"$( base64 testing/test_imgs/01.png)"'", "secret_key" : "'"$MSHACK_KEY"'"}'\
	http://127.0.0.1:5000/getnotes
}

run_flask(){
	export FLASK_APP=API/__init__.py
	export FLASK_ENV=development
	flask run
}

send_post_to_prod(){
	curl -X POST -H "Content-Type: application/json" -d \
	'{"image" : "'"$( base64 testing/test_imgs/01.png)"'", "secret_key" : "'"$MSHACK_KEY"'"}'\
	http://40.121.3.69/getnotes
}
$@
