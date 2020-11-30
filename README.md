# gwosc_external_catalogues

## TODO
- look at what's available through GWOSC for O1/O2; basically, this json file:
  https://www.gw-openscience.org/eventapi/json/GWTC/
- Download the online catalogs from IAS and 1-OGC and 2-OGC
  https://pycbc.org/pycbc/latest/html/catalog.html
  https://gwcatalog.org/
  https://github.com/jroulet/O2_samples - dunno if there's a better source for the IAS events
- Package it up to look similar to the GWOSC json. 

```
ipython notebook that 
(a) creates the json from the 3rd party catalog, and 
(b) has an example for GWOSC users of how to read in and parse the contents, make some plots, etc.

It might start with something like:

# Fetch the catalog json file
# wget https://www.gw-openscience.org/eventapi/json/GWTC-2/ -O GWOSC_GWTC-2.json
# Read in the catalog json file
import json
fnjson = 'GWOSC_GWTC-2.json'
fj = open(fnjson,'r')
cat = json.load(fj)
# print out the events in the catalog
events = cat['events'].keys()
print('Nevents =',len(events),'in',fnjson)
for event in events:
    evd = cat['events'][event]
    print(event,evd['GPS'],evd['mass_1_source'],evd['mass_2_source'],evd['network_matched_filter_snr'],evd['far'])
```


## Notes:
PyCBC package does not have info on OGC1/OGC2
- https://pycbc.org/pycbc/latest/html/catalog.html
- https://github.com/gwastro/pycbc/blob/master/pycbc/catalog/catalog.py