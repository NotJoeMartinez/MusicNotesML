
send_post(){
	rm API/uploads/*.png
	rm API/predictions/output/*.png
	rm API/predictions/output/*.txt
	uuid=$(uuidgen)
	curl -X POST -H "Content-Type: application/json" -d \
	'{"image" : "'"$( base64 testing/testing_imgs/01.PNG)"'", "secret_key" : "'"$MSHACK_KEY"'", "'"instrament"'": "'"tuba"'"}'\
	http://127.0.0.1:5000/getnotes >> testing/api_testing_imgs/$uuid.json

	python testing/test_api.py -jp testing/api_testing_imgs/$uuid.json
	rm testing/api_testing_imgs/*.json
}

run_flask(){
	export FLASK_APP=API/__init__.py
	export FLASK_ENV=development
	flask run
}

test_prod(){
	uuid=$(uuidgen)
	curl -X POST -H "Content-Type: application/json" -d \
	'{"image" : "'"$( base64 testing/testing_imgs/05.PNG)"'", "secret_key" : "'"$MSHACK_KEY"'", "'"instrament"'": "'"tuba"'"}'\
	http://40.121.3.69/getnotes >> testing/api_testing_imgs/$uuid.json

	python testing/test_api.py -jp testing/api_testing_imgs/$uuid.json

	
}


test_dir(){
	rm testing/testing_output/*.png
	rm testing/testing_output/*.txt
	python cli.py -i testing/testing_imgs -o testing/testing_output
}

test_one(){
	rm testing/testing_output/*.png
	rm testing/testing_output/*.txt
	# python cli.py -f testing/testing_imgs/02.PNG
	# python cli.py -f testing/testing_imgs/03.PNG
	python cli.py -f testing/testing_imgs/04.PNG
}


$@
