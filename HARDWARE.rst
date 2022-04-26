Hardware setup
==============

The following is some recommendations for hardware setup, although this code should be able to run on most computers with an attached webcam.

- Raspberry Pi 3A+ (or better - 4B (4GB) recommended for full resolution)

  The current setup at Imperial Physics uses Raspberry Pis for the timelapse cameras, together with a central server for some extra processing. The cameras run Raspbian Linux, while the server runs Oracle Linux, but this code should run on any modern Linux with python 3.

  Most RPi version should be capable for taking an image every 5 seconds at full resolution. The limiting factor appears to be the video creation setup using ffmpeg. An RPi 3A+ can do the video conversion at 640x480 resolution, but will struggle at 1280x960. For anything more than 480p, if you want to create timelapse videos on-camera (recommended over storing the images) an RPi 4B is recommended

- RPi camera module V2.1 (or RPi HQ camera)

  The RPi camera module V2.1 has been reasonably well characterised (Pagnutti et al, 2017. doi:10.1117/1.JEI.26.1.013014) and has good camera-to-camera repeatability. The HQ camera allows a variety of different lenses to be fitted, which may be useful for other applications. These would require separate calibrations.

- Tripod/stand for camera

  It is important that the camera extrinsic parameters (translation, rotation) remain constant for the timelapse. A simple tripod should be enough as the camera is lightweight. We have used these successfully over 6 months

  https://thepihut.com/products/modmypi-mini-camera-stand-no-lens

  https://thepihut.com/products/flexible-camera-tripod

  which also requires

  https://thepihut.com/products/camera-tripod-nuts-5-pack

- GPS module (optional, for time synchronisation)

  If time needs to be matched externally, NTP works (as long as you have a network connection). If you are working without a network (or somewhere that blocks NTP), a GPS module can provide that time signal. We have used the Adafruit Ultimate GPS HAT, but others should work too.

  https://www.adafruit.com/product/2324
  
- SDR (optional, for ADS-B reception)

  ADS-B data is available online, but if you want to receive it locally, you can use a software defined radio. RTL-SDR.com has suggestions for a variety of USB dongles that work with Linux.

