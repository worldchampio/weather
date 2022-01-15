cd src

rm Plot.png

source env/bin/activate

#pip list > dependencies.txt

python3 weather.py

deactivate

eog Plot.png
