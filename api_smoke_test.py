"""Runtime smoke test for a running Quant Research Lab server."""
import json
import os
from urllib.error import HTTPError
from urllib.request import urlopen

BASE = os.environ.get('QUANT_ENGINE_URL', 'http://127.0.0.1:4173').rstrip('/')

def get(path):
    with urlopen(BASE + path, timeout=45) as response:
        return response.status, json.loads(response.read().decode('utf-8'))

def main():
    _, health = get('/api/health')
    _, manifest = get('/api/manifest')
    assert health['status'] == 'ok' and health['version'] == manifest['version']
    assert len(manifest['tools']) == 8
    invalid_paths = [
        '/api/report',
        '/api/report?period=%3Cb%3E&universe=smoke&risk=balanced',
        '/api/report?period=' + ('x' * 257) + '&universe=smoke&risk=balanced',
    ]
    for path in invalid_paths:
        try:
            get(path)
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError(f'invalid inputs must return HTTP 400: {path}')
    status, report = get('/api/report?period=smoke&universe=smoke&risk=balanced')
    assert status == 200 and report['chain_completed']
    assert len(report['execution_ledger']) == 9
    assert report['trace_id'] == report['report']['trace_id']
    assert isinstance(report['cache_hit'], bool)
    assert isinstance(report['execution_ms'], int) and report['execution_ms'] >= 0
    _, fresh = get('/api/report?period=smoke&universe=smoke&risk=balanced&fresh=1')
    assert fresh['cache_hit'] is False and fresh['execution_ms'] >= 0
    print('api smoke test passed: validation, report, ledger, trace, cache')

if __name__ == '__main__':
    main()
