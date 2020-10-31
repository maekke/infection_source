#!/bin/bash

cantons=(
	ag
	bs
	sh
	zg
	zh
)

if [[ ${1} == "--manual" ]] ; then
	cantons=(
		ge
		sz
		vs
	)
fi

for canton in ${cantons[*]} ; do
	echo "running canton: ${canton}"
	out_file="infection_source_${canton}.csv"
	if [[ ! -f ${out_file} ]] ; then
		python scrapers/print_header.py > ${out_file}
	fi
	python scrapers/scrape_${canton}.py > tmp.csv
	new_items=$(cut -d ',' -f 1-4 tmp.csv | sort | uniq)
	for new_item in ${new_items} ; do
		echo "removing items with: ${new_item}"
		sed -i -e "/^${new_item}/d" ${out_file}
	done

	cat tmp.csv >> ${out_file}
	head -n 1 ${out_file} > tmp.csv
	tail -n +2 ${out_file} | sort >> tmp.csv
	mv tmp.csv ${out_file}
done
