# PB Forgery Detection
Source code of the article ''Forgery detection in digital images by multi-scale noise estimation".

## About the forgery-detection method

A complex processing chain is applied from the moment a raw image is acquired until1the final image is obtained. This process transforms the originally Poisson-distributed noise into a complex noise model. Noise inconsistency analysis is a rich source for forgery detection, as forged regions have likely undergone a different processing pipeline or out-camera processing. We propose a multi-scale approach which is shown to be suitable for analyzing the highly correlated noise present in JPEG-compressed images. We first estimate a noise curve for each image block, in each color channel and at each scale. Comparing each noise curve to its corresponding noise curve obtained from the whole image yields crucial detection cues. Indeed, many forgeries create a local noise deficit. Our method is shown to be competitive with the state of the art.

<p align="center"> <img src="https://user-images.githubusercontent.com/47035045/120171886-ca9de280-c202-11eb-90a9-6b23e8b7491b.png" width="50%"> </p>

## How to run the code
The compiling instruction for the Ponomarenko et al noise estimation method is just `make` from the directories where the Makefiles are ("ponomarenko/" and "ponomarenko_extract/").

The libraries needed to run the program are listed in the file requirements.txt.
You can do the following to install them in a virtual environment (venv):

Install Python 3 and upgrade pip:

`sudo apt-get update`

`sudo apt-get install -y python3 python3-dev python3-pip python3-venv`

`pip install --upgrade pip`

Create the venv, activate it, and install the requirements:

`python3 -m venv ./venv`

`source ./venv/bin/activate`

`pip3 install -r requirements.txt`

Run the code with the image to analyze as argument:

`./PB.py <input image>`

The algorithm will create a folder (“results/”) which contains the results.

Example:

`source ./venv/bin/activate` 

`./PB.py images/example.jpg` 

After the execution, the “results/” folder will contain a subdirectory "example/" containing the output heatmap (PB3.png).
