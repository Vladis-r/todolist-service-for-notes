import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register_user(client):
    response = client.post(reverse("signup"), data=dict(
        username="test_user",
        password="super_!?secret@@password--",
        password_repeat="super_!?secret@@password--"
    ))

    expected_response = dict(
        id=response.data.get("id"),
        username="test_user",
        first_name="",
        last_name="",
        email="",
        date_joined=response.data.get('date_joined'),
        last_login=None,
        is_superuser=False,
        is_staff=False,
        is_active=False,
        groups=[],
        user_permissions=[]
    )

    assert response.status_code == 201
    assert response.data == expected_response


@pytest.mark.django_db
def test_register_user_short_pass(client):
    response = client.post(reverse("signup"), data=dict(
        username="test_user",
        password="q!1",
        password_repeat="q1!"
    ))
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_user_numeric_pass(client):
    response = client.post(reverse("signup"), data=dict(
        username="test_user",
        password="1264516346836284632757247",
        password_repeat="37461386461541631263567"
    ))
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_user_do_not_match_pass(client):
    response = client.post(reverse("signup"), data=dict(
        username="test_user",
        password="qweuhqwuieh21321321!#2",
        password_repeat="jgoijroi**7##41"
    ))
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_user_already_exists(client):
    response = client.post(reverse("signup"), data=dict(
        username="test_user",
        password="qweuhqwuieh21321321!#2",
        password_repeat="qweuhqwuieh21321321!#2"
    ))

    response_again = client.post(reverse("signup"), data=dict(
        username="test_user",
        password="jdihefeih374h",
        password_repeat="jdihefeih374h"
    ))
    assert response_again.status_code == 400
