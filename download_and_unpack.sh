mkdir -p data/pycbc_search data/ias_search data/lvc_search/gwtc1 data/lvc_search/gwtc2 data/bilby/gwtc1/
cat data_files.txt | xargs -n 3 -P 2 wget -q --show-progress
unzip data/bilby/gwtc1/pesummary_samples.zip -q -d data/bilby/gwtc1/