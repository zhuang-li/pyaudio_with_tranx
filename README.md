1. ensure you have conda
2. conda env create -f audio_tranx_settings.yml
3. ./pull_data.sh
4. mv iata.txt data/atis/iata.txt
5. source activate audio_tranx
6. config your google cloud "https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries", it requires the credit card
7. download your GOOGLE_APPLICATION_CREDENTIALS key file
8. export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key_file"
9. python2 server/run_app.py --config_file data/server/config_py2.json # it would run the atis domain, which has been fully tested
10. say something like "show me the flight from seattle to san francisca"
11. the hypothesis would be on the console