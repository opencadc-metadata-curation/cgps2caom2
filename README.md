# cgps2caom2
Application to generate a CAOM2 observation from CGPS FITS files

# How cgps2caom2 works

## What does this program do

This program creates CAOM2 observations (see http://www.opencadc.org/caom2/) from FITS files from DRAO observations. It does this by creating or augmenting an Observation, which can then be dumped to stdout or to disk, in xml format. 

The python module fits2caom2, from the package caom2utils, uses a blueprint, embodied in the ObsBlueprint class, to define defaults, overrides, and FITS keyword mappings that correspond to CAOM2 entities and attributes. 

The cgps2caom2 application creates an instance of the ObsBlueprint class for each file, customizes the blueprint according to the file type and content, and then relies on fits2caom2 to do the actual CAOM2 Observation creation. 

The cgps2caom2 application assumes that all files that make up a single CGPS observation are provided on the command line at once. For example, the following invocation will create all the planes, artifacts, parts, and chunks that make up the observation 'MD1_IRAS':

<pre>
cgps2caom2 --debug --local /tmp/data/MD1_IRAS/CGPS_MD1_012_um_fwhm.txt /tmp/MD1_IRAS/CGPS_MD1_060_um_phn.fits /tmp/MD1_IRAS/CGPS_MD1_100_um_fwhm.txt /tmp/MD1_IRAS/CGPS_MD1_100_um_phn.fits /tmp/MD1_IRAS/CGPS_MD1_100_um_cfv.fits /tmp/MD1_IRAS/CGPS_MD1_012_um_phn.fits /tmp/MD1_IRAS/CGPS_MD1_060_um_cfv.fits /tmp/MD1_IRAS/CGPS_MD1_100_um_beams.fits /tmp/MD1_IRAS/CGPS_MD1_060_um_image.fits /tmp/MD1_IRAS/CGPS_MD1_012_um_beams.fits /tmp/MD1_IRAS/CGPS_MD1_012_um_image.fits /tmp/MD1_IRAS/CGPS_MD1_060_um_beams.fits /tmp/MD1_IRAS/CGPS_MD1_100_um_image.fits /tmp/MD1_IRAS/CGPS_MD1_025_um_beams.fits /tmp/MD1_IRAS/CGPS_MD1_025_um_fwhm.txt /tmp/MD1_IRAS/CGPS_MD1_025_um_cfv.fits /tmp/MD1_IRAS/CGPS_MD1_025_um_image.fits /tmp/MD1_IRAS/CGPS_MD1_060_um_fwhm.txt /tmp/MD1_IRAS/CGPS_MD1_025_um_phn.fits /tmp/MD1_IRAS/CGPS_MD1_012_um_cfv.fits --observation CGPS MD1_IRAS -o /tmp/MD1_IRAS/MD1_IRAS.actual.xml ignored_product_id ad:CGPS/CGPS_MD1_012_um_fwhm.txt ad:CGPS/CGPS_MD1_060_um_phn.fits ad:CGPS/CGPS_MD1_100_um_fwhm.txt ad:CGPS/CGPS_MD1_100_um_phn.fits ad:CGPS/CGPS_MD1_100_um_cfv.fits ad:CGPS/CGPS_MD1_012_um_phn.fits ad:CGPS/CGPS_MD1_060_um_cfv.fits ad:CGPS/CGPS_MD1_100_um_beams.fits ad:CGPS/CGPS_MD1_060_um_image.fits ad:CGPS/CGPS_MD1_012_um_beams.fits ad:CGPS/CGPS_MD1_012_um_image.fits ad:CGPS/CGPS_MD1_060_um_beams.fits ad:CGPS/CGPS_MD1_100_um_image.fits ad:CGPS/CGPS_MD1_025_um_beams.fits ad:CGPS/CGPS_MD1_025_um_fwhm.txt ad:CGPS/CGPS_MD1_025_um_cfv.fits ad:CGPS/CGPS_MD1_025_um_image.fits ad:CGPS/CGPS_MD1_060_um_fwhm.txt ad:CGPS/CGPS_MD1_025_um_phn.fits ad:CGPS/CGPS_MD1_012_um_cfv.fits
</pre>

## How to install this program

Use github until the pypi versons of the caom2 and caom2utils packages catch up with the latest work.

Works with python 2.7, 3.6.3.

<pre>
git clone https://github.com/SharonGoliath/caom2tools &amp;&amp; \
  cd caom2tools &amp;&amp; \
  git checkout s2226 &amp;&amp; \
  pip install ./caom2 &amp;&amp; \
  pip install ./caom2utils
pip install git+https://github.com/SharonGoliath/cgps2caom2.git@s2232
</pre>

## How to use this program

<pre>
usage: cgps2caom2 [-h] [-V] [-d | -q | -v] [--dumpconfig] [--ignorePartialWCS]
                  [-o OUT_OBS_XML]
                  (-i IN_OBS_XML | --observation collection observationID)
                  [--local LOCAL [LOCAL ...]] [--log LOG] [--keep] [--test]
                  [--cert CERT]
                  productID fileURI [fileURI ...]

Augments an observation with information in one or more fits files.

positional arguments:
  productID             product ID of the plane in the observation
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
FROM python:3.6.3-jessie

WORKDIR /usr/src/app

RUN git clone https://github.com/SharonGoliath/caom2tools &amp;&amp; \
  cd caom2tools &amp;&amp; \
  git checkout s2226 &amp;&amp; \
  pip install ./caom2 &amp;&amp; \
  pip install ./caom2utils
RUN pip install git+https://github.com/SharonGoliath/cgps2caom2.git@s2232

COPY ./docker-entrypoint.sh ./

ENTRYPOINT ["./docker-entrypoint.sh"]
</pre>

* run the build (tagged with the name cgps2caom2-363):

<pre>docker build -t cgps2caom2-363 -f Dockerfile ./</pre>

* run the application, using the docker image tagged with the name cgps2caom2-363:

<pre>docker run --rm -ti cgps2caom2-363 cgps2caom2 &lt;arguments&gt;
</pre>

### Test the application

* run the application:

<pre>cgps2caom2 --observation CGPS MC5_IRAS -o ./MC5_408.actual.xml ignored_product_id ad:CGPS/CGPS_MC5_408_MHz_image.fits</pre>

* or run the application using docker:

  * no mount required
<pre>docker run --rm -ti cgps2caom2-363 cgps2caom2 --observation CGPS MC5_IRAS ignored_product_id ad:CGPS/CGPS_MC5_408_MHz_image.fits</pre>  

  * with a mount
  
<pre>docker run --rm -v &lt;cwd&gt;:/usr/src/app/test_data -ti cgps2caom2-363 cgps2caom2 --observation CGPS MC5_IRAS -o /usr/src/app/test_data/MC5_IRAS.actual.xml ignored_product_id ad:CGPS/CGPS_MC5_408_MHz_image.fits</pre>
