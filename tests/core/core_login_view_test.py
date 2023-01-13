import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_user(client, create_user):
    response = client.post(reverse("login"), data=dict(
        username="test_user",
        password="secret@@pass"
    ))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_user_wrong_pass(client, create_user):
    response = client.post(reverse("login"), data=dict(
        username="test_user",
        password="wrong_secret74pass"
    ))
    assert response.status_code == 403


@pytest.mark.django_db
def test_login_user_wrong_username(client, create_user):
    response = client.post(reverse("login"), data=dict(
        username="test_user2",
        password="secret@@pass"
    ))
    assert response.status_code == 403
