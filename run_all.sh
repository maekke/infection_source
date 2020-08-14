#!/bin/bash

cantons=(
	ag
	zg
	zh
)

for canton in ${cantons[*]} ; do
	echo "running canton: ${canton}"
	out_file="infection_source_${canton}.csv"
	if [[ ! -f ${out_file} ]] ; then
		python scrapers/print_header.py > ${out_file}
	fi
	python scrapers/scrape_${canton}.py >> ${out_file}
	head -n 1 ${out_file} > tmp.csv
	tail -n +2 ${out_file} | sort | uniq >> tmp.csv
	mv tmp.csv ${out_file}
done
