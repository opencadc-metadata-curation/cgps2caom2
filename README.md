# cgps2caom2
Application to generate a CAOM2 observation from CGPS FITS files

# How cgps2caom2 works

## What does this program do

This program creates CAOM2 observations (see http://www.opencadc.org/caom2/) from FITS files from DRAO observations. It does this by creating or augmenting an Observation, which can then be dumped to stdout or to disk, in xml format. 

The python module fits2caom2 uses a blueprint, embodied in the ObsBlueprint class, to define defaults, overrides, and FITS keyword mappings that correspond to CAOM2 entities and attributes. See the section 

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
 
* create a Dockerfile referencing your favourite python version (uses github because the pypi versons of the packages aren't the latest, does not result in the smallest possible container):

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

* run the build (tagged with the name cgps2caom2-27):

<pre>docker build -t cgps2caom2-27 -f Dockerfile ./</pre>

* run the application, using the docker image tagged with the name cgps2caom2-27:

<pre>docker run --rm -ti cgps2caom2-27 cgps2caom2 &lt;arguments&gt;
</pre>

### Test the application

* get a test file:

<pre>cadc-data get CGPS CGPS_MC5_408_MHz_image.fits</pre>

* run the application:

<pre>cgps2caom2 --local ./CGPS_MC5_408_MHz_image.fits  --observation CGPS MD1_IRAS -o ./MC5_408.actual.xml ignored_product_id ad:/CGPS/CGPS_MC5_408_MHz_image.fits</pre>

* or run the application using docker:

<pre>docker run --rm -v &lt cwd &gt:/usr/src/app/test_data -ti cgps2caom2-27 cgps2caom2 --local /usr/src/app/test_data/CGPS_MC5_408_MHz_image.fits  --observation CGPS MD1_IRAS -o /usr/src/app/test_data/MC5_IRAS.actual.xml ignored_product_id ad:/CGPS/CGPS_MC5_408_MHz_image.fits</pre>

# How cgps2caom2 organizes DRAO Observations into CAOM2 Observations (Russell Redmond)

1. CGPS data

The CGPS archive contains files from 3 observatories:
* DRAO ST 408 and 1420 continuum and H I 21cm datacubes
* IRAS processed through HIRES
* FCRAO CO datacubes

These all need to be ingested into the same CAOM database.  They have a common file format, which is discussed in the next sections.

1.1. OBSERVATION

 There is no raw data in the archive, so all observations are simple.

 A simple observation is made of a particular target using a specified telescope and instrument and at a particular time.  We need to distinguish DRAO, IRAS and FCRAO observations.

 The archive, collection and project will all be the same, CGPS.

 There is no associated project metadata.

 The telescope can be derived from the INSTRUME header, but should not be used verbatim.  This header is unambiguous for "DRAO ST" and "FCRAO 14-m Tel", but the IRAS reprocessed data are listed as "IPAC HiRES" and "IPAC/UT HIRES", which refer to the data processing, not to the telescope (IRAS).  To handle these cases, the telescope fields should be filled in the override file with values  ("DRAO ST", "FCRAO", "IRAS") interpreted from the INSTRUME header.

 The target name is contained in the ADC_AREA header (not the OBJECT header) for CGPS data.

 For these data, the instrument is the same as the telescope.  This is not the intended usage, but is the clear implication of the use of the INSTRUME to supply the telescope name.

 The DRAO 408 cont, 1420 cont and 1420 21cm data are taken simultaneously and therefore qualify as three distinct wavelength bands within a single observation.  They are, however, processed quite separately.  Since these data are processed data, not raw, it is important to distinguish the processing dates by recorded them in separate planes.

 Upon further discussion, it is useful to record the different vavelength bands and image products in different observations, except for IRAS which will follow the IRIS convention of grouping the wavelength bands into a single plane.  The auxiliary files (if any) will be recorded in separate planes in the same observation and marked as siblings of the image in the provenance tables.

 The IRAS 12, 25, 60 and 100 micron bands images of each field belong in the same observation, and following the examples of other instances of the IRAS data in the CADC (e.g. IRIS) the four wavebands will be recorded as four artifacts in a single plane.

 So far as I have been able to determine, all the data files for a particular target made with a particular telescope record the same DATE-OBS.  If this is not true, it will be necessary to divide the observations by DATE-OBS.

 With these considerations, the collectionID can be generated by joining the target name, band and telescope, as in:

    "MEV1_408_DRAO_ST"

1.2. PLANES

 Release date is given in PUB_RELD for CGPS data.  There is no corresponding date in the VGPS headers, but DATE-OBS can be used because the data are all public now.

 There are several different "products" in each CGPS observation.  For the IRAS observations it is sensible to collect the 4 bands together into the same plane because they are guaranteed not to share photons.  Similarly, the continuum images for the ST observations could be grouped into the same plane, because they have identical physical metadata except for wavelength and are guaranteed not to share photons.  However, the release_date (ADC_RELD) is different for the two continuum images. DRAO believes that this is important, so the products should be kept in different planes.  We can use ADC_QUAL (qualifier) to distinguish planes.  Note that cubes and images are not distinguished by ADC_QUAL, but because the different bands (408, 1420, HI, etc.) already put these in different observations, there is no conflict.

 Those planes with ADQ_QUAL = "image" should have observable_ctype="CAL", otherwise observable_ctype="AUX".

 The BUNIT header uses non-standard units, where it is defined at all, and will need to be translated into more standard units before filling observable_cunit:

     MJY/STER -> MJy/ster
     "K (Tb)" -> "K"
     "K"      -> "K"
     else leave NULL

1.3. ARTIFACTS

 There is no indication of how long the observations took.  Note that DATE-OBS is nominally the mean date of the observation, in spite of the FITS standard that indicates it should be the starting datetime.

 Worse, DATE-OBS is not reliable and sometimes records "mean observation dates" that are still in the future (e.g. 2020-01-01) even though the data have been public for five years already.  We have no source of observing date/time information and will omit time structures.

 Positional WCS is given by the standard headers, in galactic cartesian coordinates.  In cartesian coordinates along an equatorial strip it should be true that CD1_1 = CDELT1 and CD2_2=CDELT2.

 Energy WCS is more problematic, since it is not consistent.  For the 408 MHz data there is only one channel, centered on 408.0 MHz.  CDELT3 does NOT tell us the bandwidth, which is 4 MHz for the 408 MHz image and 30 MHz for the 1420 MHz image.  The (completely non-standard) band name is contained in the ADC_BAND header.  For the H I and CO cubes, the energy axis is given in CTYPE3 = 'VELO-LSR' (should have been 'VELO-F2V' with SPECSYS='LSRK') swith a reference frequency in the header OBSFREQ.

 The fourth (polarization) axis is defined for all file types, but the ADC_POLR header is defined only for a few of them.  It is probably safest to leave the CAOM polarization structure undefined except when this header is defined.

1.4. PROCESSING

 Each plane should have its own process, recording the date the processing ran.

 The value of prov_process.name can be filled with the concatenation of the values of ADC_ARCH and ADC_TYPE for the DRAO and FCRAO data, and with the fixed value "CGPS MOSAIC HIRES" for the IRAS data.

 The field prov_process.reference should be:
  
    'http://dx.doi.org/10.1086/375301'

 The field proc_process.producer can be filled from the header OBSERVER.

 The value of proc_process.version should always be 1.

 The field prov_process.lastExecuted can be taken from the header DATE-FTS.

 The field prov_output.name can be filled from the header IMAG_DES.
 
 The field prov_output.version is always 1.

2. VGPS data

 The VGPS data is not recorded in a database.  The interface is hard-coded in html.  It should be straight-forward to ingest these files into the cgps database in caom, setting the collection to CGPS or VGPS appropriately.

 Each target has three associated files (artifacts), each of which will sit in its own plane.  File structure is similar to the CGPS, but 3-D rather than 4-D (no polarization).  There are fewer program headers in the files.  The ADC headers in particular are missing.  Some of the headers have different names, so the associated metadata will need to be handled through the override file.

2.1. OBSERVATIONS

 As for CGPS, INSTRUME identifies the telescope (VLA).

 The archive, collection and project will all be the same, VGPS.

 The OBJECT header is clearly intended to represent an (l, b) coordinate, but bears no obvious relationship to the actual coordinates of the center of the image.  For example, the three files MOS_017.Tb.fits, MOS_017_cont.Tb.fits and MOS_017_contincluded.Tb.fits have the OBJECT values l018b04b, l001b04a and l017b04b, respectively, although they all have the same galactic longitude.

 We will use the same target name used to identify each field in the current  VGPS UI, which is just the first 7 characters of each file name.  These have the form 'MOS_nnn' where nnn is the galactic longitude of the center position.

 Following the pattern of the CGPS observations, the collectionID will be the join of the target name and telescope.  There are 13 observations that can be identified by this collectionID in the VGPS collection.

 There is no associated project metadata.

 The target classification is always 'FIELD'.

2.2. PLANES

 There is no explicit release date for the VGPS data, but DATE-OBS can be used because the data are all public now.

 There are three different "products" in each VGPS observation, and H I datacube with the continuum subtracted, a continuum image and an H I datacube with the continuum included.  Oddly, the H I datacube with continuum subtracted is NOT a sibling of the other two (and has no siblings), but is a product of independent processing.

 Those planes with ADQ_QUAL = "image" should have observable_ctype="CAL" for all three kinds of file.

 The BUNIT header is always 'K', correct for these data.

2.3. ARTIFACTS

 There is no indication of how long the observations took.  For the VGPS data,  DATE-OBS seems more reliable than for the CGPS data, but it remains unclear whether it is the start, mean or end time of the observations.  As for the CGPS data, we will omit time structures.

 Positional WCS is given by the standard headers, in galactic cartesian coordinates.  In cartesian coordinates along an equatorial strip it should be true that CD1_1 = CDELT1 and CD2_2=CDELT2.

 Energy WCS is given in VLSR with a rest frequency in the header FREQ0.

 The fourth (polarization) axis is nominally defined as I, but it is unclear whether this is measured as part of a polarization observation, or merely assumed.  The polarization structure will be left undefined.

2.4. PROCESSING

 Each plane should have its own process, chiefly to record the date the processing ran. The processing name is contained in the ORIGIN keyword.  Note that this is different from the CGPS.

 The value of prov_process.name can be filled from the ORIGIN header.

 The value of proc_process.version should always be 1.

 The reference for the VLA data should be to:
    
    http://dx.doi.org/10.1086/505940

 The field prov_process.producer is defined for the VGPS data in the HISTORY cards to be:

    "VLA Galactic Plane Survey (VGPS) Consortium"

 The field prov_process.lastExecuted cannot be filled for VGPS data.  To leave this field null, it is sufficient to fill it from the header DATE-FTS, as is done for CGPS data.  Since this header does not exist for the VGPS data, the field will be left null.

 The prov_output.name. field can be derived from the file name.  I have translated the file_id's into the three values:

     <target.name>.Tb              -> 'VLA cube'
     <target.name>_cont.Tb         -> 'VLA continuum'
     <target.name>_contincluded.Tb -> 'VLA cube with continuum'

 The value of prov_output.version is always 1.
