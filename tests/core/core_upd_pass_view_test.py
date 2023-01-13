import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profile_update_pass(authenticated_user):
    response = authenticated_user.put(reverse("update_password"), data=dict(
        old_password="secret@@pass",
        new_password="secret@@password"
    ))

    expected_response = authenticated_user.post(reverse("login"), data=dict(
        username="login_user",
        password="secret@@password"
    ))

    assert response.status_code == 200
    assert expected_response.status_code == 200
