def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'

def test_add_trade(client):
    trade_data = {
        'data': 'Pair: EUR/USD\nVerdict: Win\nEntry Price: 1.0845\nStop-Loss: 1.0800\nTarget/Exit Price: 1.0900'
    }
    response = client.post('/webhook', json=trade_data)
    assert response.status_code == 200
    assert b'Trade added successfully' in response.data
