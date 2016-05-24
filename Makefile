testpy2:
	conda create --yes --name testpy2 python=2; \
	source activate testpy2; \
	conda install --yes numpy scipy; \
	pip install --upgrade pip; \
	pip install nose-cov; \
	python setup.py install; \
	nosetests --with-cov --cov gazelib --logging-level=INFO; \
	source deactivate > /dev/null; \
	conda remove --yes --name testpy2 --all > /dev/null

testpy3:
	conda create --yes --name testpy3 python=3; \
	source activate testpy3; \
	conda install --yes numpy scipy; \
	pip install --upgrade pip; \
	pip install nose-cov; \
	python setup.py install; \
	nosetests --with-cov --cov gazelib --logging-level=INFO; \
	source deactivate > /dev/null; \
	conda remove --yes --name testpy3 --all > /dev/null

quicktestpy2:
	source activate gazepy2; \
	nosetests --with-cov --cov gazelib --logging-level=INFO; \
	source deactivate; \

quicktestpy3:
	source activate gazepy3; \
	nosetests --with-cov --cov gazelib --logging-level=INFO; \
	source deactivate; \
