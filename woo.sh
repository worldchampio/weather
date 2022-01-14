cd src

rm Plot.png

source env/bin/activate

python3 weather.py

deactivate

eog Plot.png
