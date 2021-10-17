rm testing/testing_output/*.png
rm testing/testing_output/*.txt

test_dir(){
	python cli.py -i testing/testing_imgs -o testing/testing_output
}

test_one(){
	# python cli.py -f testing/testing_imgs/02.PNG
	# python cli.py -f testing/testing_imgs/03.PNG
	python cli.py -f testing/testing_imgs/04.PNG
}


$@