def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'

def test_add_trade(client):
    trade_data = {
        'Pair': 'EUR/USD',
        'Verdict': 'Win',
        'Entry Price': '1.0845',
        'Stop-Loss': '1.0800',
        'PnL': 25.3
    }
    response = client.post('/webhook', json=trade_data)
    assert response.status_code == 200
    assert b'Trade added successfully' in response.data
