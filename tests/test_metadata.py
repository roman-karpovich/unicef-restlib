import pytest
from demo.sample.metadata import ImageFileTypeMetadata, ReadOnlyChoiceMetadata, SeparateReadWriteMetadata
from demo.sample.serializers import (
    AuthorSerializer,
    BookSeparatedSerializer,
    ImageFileTypeChoiceSerializer,
    ImageFileTypeSerializer,
)
from django.urls import reverse
from tests.factories import FileTypeFactory

pytestmark = pytest.mark.django_db


def test_model_choice_field_metadata():
    file_type = FileTypeFactory(code="image")
    file_type_wrong = FileTypeFactory(code="wrong")
    serializer = ImageFileTypeSerializer()
    metadata = ImageFileTypeMetadata().get_serializer_info(serializer)
    file_type_choices = [x['value'] for x in metadata['file_type']['choices']]
    assert file_type.pk in file_type_choices
    assert file_type_wrong.pk not in file_type_choices


def test_read_only_choice_field_metadata():
    serializer = ImageFileTypeChoiceSerializer()
    metadata = ReadOnlyChoiceMetadata().get_serializer_info(serializer)
    file_type_choices = [x['value'] for x in metadata['file_type']['choices']]
    assert file_type_choices == [1, 2]


def test_separated_read_write_field_metadata(rf):
    request = rf.options(reverse("sample:author-list"))
    serializer = BookSeparatedSerializer(context={"request": request})
    metadata = SeparateReadWriteMetadata().get_serializer_info(serializer)
    assert "author" in metadata


def test_cru_actions_metadata(client):
    response = client.options(reverse("sample:authors-meta-cru"))
    assert response.status_code == 200
    data = response.json()
    assert list(data["actions"].keys()) == ["GET"]


def test_fsm_transition_actions_metadata_no_actions(client, superuser):
    client.force_login(superuser)
    response = client.options(reverse("sample:authors-meta-fsm-list"))
    assert response.status_code == 200
    assert "actions" not in response.json()


def test_fsm_transition_actions_metadata_no_status(client, superuser, author):
    client.force_login(superuser)
    response = client.options(
        reverse("sample:authors-meta-fsm", args=[author.pk])
    )
    assert response.status_code == 200
    data = response.json()
    assert list(data["actions"].keys()) == ["PUT"]


def test_fsm_transition_actions_metadata(client, superuser, review):
    client.force_login(superuser)
    response = client.options(
        reverse("sample:review-meta-fsm", args=[review.pk])
    )
    assert response.status_code == 200
    data = response.json()
    assert list(data["actions"].keys()) == ["PUT", "allowed_FSM_transitions"]
