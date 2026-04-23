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

## Dependencies

External libraries used:
- requests
- pytest
- pytest-cov
- ruff

```bash
pip install -r requirements.txt