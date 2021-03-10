progressfilt ()
{
    local flag=false c count cr=$'\r' nl=$'\n'
    while IFS='' read -d '' -rn 1 c
    do
        if $flag
        then
            printf '%s' "$c"
        else
            if [[ $c != $cr && $c != $nl ]]
            then
                count=0
            else
                ((count++))
                if ((count > 1))
                then
                    flag=true
                fi
            fi
        fi
    done
}

mkdir -p data/pycbc_search data/ias_search data/lvc_search/gwtc1 data/lvc_search/gwtc2 data/bilby/gwtc1/
cat data_files.txt | xargs -n 3 -P 2 wget -q --progress=bar:force | progressfilt
unzip data/bilby/gwtc1/pesummary_samples.zip -q -d data/bilby/gwtc1/