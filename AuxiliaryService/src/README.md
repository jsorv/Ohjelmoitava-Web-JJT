# Auxiliary Service

This auxiliary service is a separate background process for the Weather Radar application.

It communicates with:
- the main API through HTTP requests
- the client through a TCP socket interface

The service periodically fetches locations and forecast data from the API and generates weather alerts such as:
- Hot
- Cold
- Strong wind
- Very humid
- Very cloudy
- Rain
- Fog

## How to test the Auxiliary Service:

1. Open Terminal 1 and go to API directory
```bash
cd \Ohjelmoitava-Web-JJT\API
```
2.  Run the API
```bash
flask --app weatherradar run
```
3. Api should start at http://localhost:5000

4. Test in browser: http://localhost:5000/weatherradar/api/locations/

5. Open Terminal 2 and go to auxiliaryService/src directory
```bash
cd \Ohjelmoitava-Web-JJT\AuxiliaryService\src
```
6. run
```bash
python main.py
```

## Run automated tests
1. Go to: 
```bash
cd \Ohjelmoitava-Web-JJT\AuxiliaryService\src
```
2. Run
```bash
pytest tests
```
## Dependencies

External libraries used:
- requests
- pytest
- pytest-cov
- ruff

```bash
pip install -r requirements.txt