vw-mib3-map-validator
=====================

This quick & dirty tool allows you to run a basic validation on a map update database for
Volkswagen MIB3 infotainment systems (Discover Media / Discover Pro).

These map update database are usually obtained from VW's website, but the file
contents can get damaged during download, extraction, while copying to the USB pen
drive or simply because VW updated an update with broken content (as observed
in the past, e.g. `EUR_6PR053_FCT3WS-201H0_Offline_Update.tar`, later fixed via
`EUR_6PR053_FCT3WS-201H0_Offline_UpdateV2.tar`).

Use cases
---------
This tool can be useful in order to:
 - Validate a downloaded map database to check it has been downloaded and extracted
   correctly and/or uploaded correctly by VW.
 - Validate a map update copied to an USB pen drive to ensure no data got corrupted
   while copying or due to a broken pen drive.
 - Validate a map update you're about to deliver to your customers when you're a big
   automotive corporation. It can save you and your customers lots of time, bandwidth
   and frustration, especially if the cars you're selling do not provide *any* way of
   monitoring the update progress and status ;-)

What is checked
---------------
The tool performs basic validation of the package table of contents, package config
files and verifies that all the embedded checksums match the actual checksums of the
files.

Prerequisites
-------------
You need python 3 and the `click` package (`pip3 install click`).

Usage
-----
1. Extract the map update tar file, if not already done.
2. Run the tool with
   `python3 ./vw-mib3-map-validator.py --folder ./path/to/extracted/tar/file/contents`

You can also invoke it directly on the mounted USB pen drive, for example:
`python3 ./vw-mib3-map-validator.py --folder /Volumes/MapUpdateUSB`

Example output
--------------
### Success case (e.g. EUR_6PR053_FCT3WS-201H0_Offline_UpdateV2.tar)
```
    Validating package: MIB31_EU.ROOT
    Validating package: ... <many more>
Validation succeeded!
This looks like a valid map update. Go ahead and try it in your vehicle!
```

### Error case (e.g. EUR_6PR053_FCT3WS-201H0_Offline_Update.tar)
```
    Validating package: MIB31_EU.ROOT
Validation failed!
This does not look like a valid map update:
  ('Failed to validate package MIB31_EU.ROOT!', MapValidationException('Checksum error in package config MIB31_EU.ROOT/PACKAGE.CFG: should = 39f2f17566f898aa3ba72c8538e301d11824a3ca26658715221d77e5529c5c3c, is = 1599f8f693f51253b2ca9abed62284080d5afc4a4ec1465fa2824122a3e85206'))
```

License
-------
Licensed under the terms of the MIT license.
