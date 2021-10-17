
import json, pathlib, argparse, base64, subprocess

def main(args):
    test_api(args.json_filepath)

def test_api(json_filepath):
    print(f"here: {json_filepath}")
    with open(json_filepath) as json_file:
        data = json.load(json_file)

    b64_str = data["b64_overylayed_img"]
    subprocess.run(f"echo {b64_str} | base64 -d -o {json_filepath[:-5]}.png ", shell=True)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-jp", "--json-filepath", action="store")
    args = parser.parse_args()

    main(args)
