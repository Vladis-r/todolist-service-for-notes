def test_pytest_install():
    assert True


# когда-нибудь он сможет вернуть 200
def test_root_not_found(client):
    response = client.get("/")
    assert response.status_code == 404
