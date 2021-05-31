# PB_Forgery_Detection
Source code of the article ''Forgery detection in digital images by multi-scale noise estimation".

## About the forgery-detection method

A complex processing chain is applied from the moment a raw image is acquired until1the final image is obtained. This process transforms the originally Poisson-distributed noise into a complex noise model. Noise inconsistency analysis is a rich source for forgery detection, as forged regions have likely undergone a different processing pipeline or out-camera processing. We propose a multi-scale approach which is shown to be suitable for analyzing the highly correlated noise present in JPEG-compressed images. We first estimate a noise curve for each image block, in each color channel and at each scale. Comparing each noise curve to its corresponding noise curve obtained from the whole image yields crucial detection cues. Indeed, many forgeries create a local noise deficit. Our method is shown to be competitive with the state of the art.

<p align="center"> <img src=![Captura de pantalla de 2021-05-31 11-22-01](https://user-images.githubusercontent.com/47035045/120171886-ca9de280-c202-11eb-90a9-6b23e8b7491b.png)
 width="50%"> </p>
