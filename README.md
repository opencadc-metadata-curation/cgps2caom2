# cgps2caom2
Application to generate a CAOM2 observation from CGPS FITS files

# How cgps2caom2 works

## What does this program do

This program creates CAOM2 observations (see http://www.opencadc.org/caom2/) from FITS files from DRAO observations. It does this by creating or augmenting an CAOM2 Observation record, which can then be dumped to stdout or to disk, in xml format.

cgps2caom2 creates the Observation record using information contained in a cgps FITS file.  The python module fits2caom2, from the python package caom2utils, examines the FITS file and uses a blueprint, embodied in an instance of an ObsBlueprint class, to define default values, override values, and mappings that connect FITS header keywords to corresponding to CAOM2 values and attributes.

The cgps2caom2 application creates an instance of the ObsBlueprint class for each file, customizes the blueprint according to the file type and content, and then calls on fits2caom2 to do the actual CAOM2 Observation creation.

The cgps2caom2 application assumes that all files that make up a CGPS CAOM2 Observation (ie, the image, weight, counts, etc.) are provided on the command line at once. For example, the following invocation will create all the planes, artifacts, parts, and chunks that make up the observation 'MD1_IRAS':

<pre>
cgps2caom2 --debug --local /tmp/data/MD1_IRAS/CGPS_MD1_012_um_fwhm.txt /tmp/MD1_IRAS/CGPS_MD1_060_um_phn.fits /tmp/MD1_IRAS/CGPS_MD1_100_um_fwhm.txt /tmp/MD1_IRAS/CGPS_MD1_100_um_phn.fits /tmp/MD1_IRAS/CGPS_MD1_100_um_cfv.fits /tmp/MD1_IRAS/CGPS_MD1_012_um_phn.fits /tmp/MD1_IRAS/CGPS_MD1_060_um_cfv.fits /tmp/MD1_IRAS/CGPS_MD1_100_um_beams.fits /tmp/MD1_IRAS/CGPS_MD1_060_um_image.fits /tmp/MD1_IRAS/CGPS_MD1_012_um_beams.fits /tmp/MD1_IRAS/CGPS_MD1_012_um_image.fits /tmp/MD1_IRAS/CGPS_MD1_060_um_beams.fits /tmp/MD1_IRAS/CGPS_MD1_100_um_image.fits /tmp/MD1_IRAS/CGPS_MD1_025_um_beams.fits /tmp/MD1_IRAS/CGPS_MD1_025_um_fwhm.txt /tmp/MD1_IRAS/CGPS_MD1_025_um_cfv.fits /tmp/MD1_IRAS/CGPS_MD1_025_um_image.fits /tmp/MD1_IRAS/CGPS_MD1_060_um_fwhm.txt /tmp/MD1_IRAS/CGPS_MD1_025_um_phn.fits /tmp/MD1_IRAS/CGPS_MD1_012_um_cfv.fits --observation CGPS MD1_IRAS -o /tmp/MD1_IRAS/MD1_IRAS.actual.xml ad:CGPS/CGPS_MD1_012_um_fwhm.txt ad:CGPS/CGPS_MD1_060_um_phn.fits ad:CGPS/CGPS_MD1_100_um_fwhm.txt ad:CGPS/CGPS_MD1_100_um_phn.fits ad:CGPS/CGPS_MD1_100_um_cfv.fits ad:CGPS/CGPS_MD1_012_um_phn.fits ad:CGPS/CGPS_MD1_060_um_cfv.fits ad:CGPS/CGPS_MD1_100_um_beams.fits ad:CGPS/CGPS_MD1_060_um_image.fits ad:CGPS/CGPS_MD1_012_um_beams.fits ad:CGPS/CGPS_MD1_012_um_image.fits ad:CGPS/CGPS_MD1_060_um_beams.fits ad:CGPS/CGPS_MD1_100_um_image.fits ad:CGPS/CGPS_MD1_025_um_beams.fits ad:CGPS/CGPS_MD1_025_um_fwhm.txt ad:CGPS/CGPS_MD1_025_um_cfv.fits ad:CGPS/CGPS_MD1_025_um_image.fits ad:CGPS/CGPS_MD1_060_um_fwhm.txt ad:CGPS/CGPS_MD1_025_um_phn.fits ad:CGPS/CGPS_MD1_012_um_cfv.fits
</pre>

## How to install this program

Works with python 2.7, 3.6 (.3 and .4).

<pre>
pip install caom2 &amp;&amp; \
  pip install caom2utils
pip install git+https://github.com/SharonGoliath/cgps2caom2.git
</pre>

## How to use this program

<pre>
usage: cgps2caom2 [-h] [-V] [-d | -q | -v] [--dumpconfig] [--ignorePartialWCS]
                  [-o OUT_OBS_XML]
                  (-i IN_OBS_XML | --observation collection observationID)
                  [--local LOCAL [LOCAL ...]] [--log LOG] [--keep] [--test]
                  [--cert CERT] [--productID PRODUCTID]
                  fileURI [fileURI ...]

Augments an observation with information in one or more fits files.

positional arguments:
  fileURI               URI of a fits file

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -d, --debug           debug messages
  -q, --quiet           run quietly
  -v, --verbose         verbose messages
  --dumpconfig          output the utype to keyword mapping to the console
  --ignorePartialWCS    do not stop and exit upon finding partial WCS
  -o OUT_OBS_XML, --out OUT_OBS_XML
                        output of augmented observation in XML
  -i IN_OBS_XML, --in IN_OBS_XML
                        input of observation to be augmented in XML
  --observation collection observationID
                        observation in a collection
  --local LOCAL [LOCAL ...]
                        list of files in local filesystem (same order as uri)
  --log LOG             log file name > (instead of console)
  --keep                keep the locally stored files after ingestion
  --test                test mode, do not persist to database
  --cert CERT           Proxy Cert&Key PEM file
  --productID PRODUCTID product ID of the plane in the observation
</pre>

### If you use docker
In an empty directory:

* create a docker-entrypoint.sh file with owner-executable permissions:

<pre>
#!/usr/bin/env bash
$@
</pre>
 
* create a Dockerfile referencing your favourite python version (does not result in the smallest possible container):

<pre>
# FROM python:2.7-jessie
FROM python:3.6-jessie

WORKDIR /usr/src/app

RUN pip install caom2 &amp;&amp; pip install caom2utils
RUN pip install git+https://github.com/SharonGoliath/cgps2caom2.git

COPY ./docker-entrypoint.sh ./

ENTRYPOINT ["./docker-entrypoint.sh"]
</pre>

* run the build (tagged with the name cgps2caom2-36):

<pre>docker build -t cgps2caom2-36 -f Dockerfile ./</pre>

* run the application, using the docker image tagged with the name cgps2caom2-36:

<pre>docker run --rm -ti cgps2caom2-36 cgps2caom2 &lt;arguments&gt;
</pre>

### Test the application

* run the application:

<pre>cgps2caom2 --observation CGPS MC5_IRAS -o ./MC5_408.actual.xml ad:CGPS/CGPS_MC5_408_MHz_image.fits</pre>

* or run the application using docker, with no mount required

<pre>docker run --rm -ti cgps2caom2-363 cgps2caom2 --observation CGPS MC5_IRAS ad:CGPS/CGPS_MC5_408_MHz_image.fits</pre>  

* run the application using docker, with a mount  
  
<pre>docker run --rm -v &lt;cwd&gt;:/usr/src/app/test_data -ti cgps2caom2-36 cgps2caom2 --observation CGPS MC5_IRAS -o /usr/src/app/test_data/MC5_IRAS.actual.xml ad:CGPS/CGPS_MC5_408_MHz_image.fits</pre>
