import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profile_update_user(authenticated_user):
    response = authenticated_user.put(reverse("profile"), data=dict(
        username="login_user",
        first_name="new_first_name",
        last_name="",
        email=""
    ))

    expected_response = dict(
        id=response.data.get("id"),
        username="login_user",
        first_name="new_first_name",
        last_name="",
        email=""
    )
    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_profile_retrieve_user(authenticated_user):
    response = authenticated_user.get(reverse("profile"))

    expected_response = dict(
        id=response.data.get("id"),
        username="login_user",
        first_name="",
        last_name="",
        email=""
    )

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_profile_logout_user(authenticated_user):
    response = authenticated_user.delete(reverse("profile"))

    assert response.status_code == 204


