
send_post(){
	# foo=$(base64 -i test_imgs/04.PNG)
	# curl -X POST \"$foo\" http://127.0.0.1:5000/get_string
	curl --data '@b64.txt' -X POST http://127.0.0.1:5000/get_string
}

run_flask(){
	export FLASK_APP=API/__init__.py
	export FLASK_ENV=development
	flask run
}

send_post
# run_flask