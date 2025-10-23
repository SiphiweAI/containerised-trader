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
    response = client.post('/add_trade', json=trade_data)
    assert response.status_code == 200
    assert b'Trade added successfully' in response.data

def test_get_trades(client):
    response = client.get('/trades')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for trade in data:
        assert 'pair' in trade
        assert 'verdict' in trade
        assert 'entry_price' in trade
        assert 'pnl' in trade

def test_invalid_trade_data(client):
    invalid_data = {
        'Pair': 'EUR/USD',
        # Missing 'Verdict'
        'Entry Price': '1.0845',
        'Stop-Loss': '1.0800',
        'PnL': 25.3
    }
    response = client.post('/add_trade', json=invalid_data)
    assert response.status_code == 400
    assert b'Invalid trade data' in response.data
