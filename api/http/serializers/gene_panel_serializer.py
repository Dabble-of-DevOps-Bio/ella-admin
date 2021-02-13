from rest_framework import serializers
from rest_framework.fields import CharField, BooleanField, DateTimeField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.user_group_serializer import UserGroupSerializer
from api.http.serializers.user_serializer import UserSerializer
from api.models import UserGroup, GenePanel, UserGroupGenePanel


class GenePanelSerializer(BaseModelSerializer):
    class Meta:
        model = GenePanel
        fields = (
            'id', 'name', 'version', 'genome_reference', 'official', 'date_created', 'user', 'groups'
        )
        expandable_fields = {
            'user': UserSerializer,
            'groups': (UserGroupSerializer, {'many': True, 'source': 'groups'}),
        }

    name = CharField(read_only=True)
    version = CharField(read_only=True)
    genome_reference = CharField(read_only=True)
    official = BooleanField(read_only=True)
    date_created = DateTimeField(read_only=True)

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    groups = serializers.PrimaryKeyRelatedField(required=False, queryset=UserGroup.objects.all(), many=True, allow_null=False, allow_empty=True)

    def create(self, validated_data):
        pass

    def update(self, instance: GenePanel, validated_data):
        if 'groups' in validated_data:
            groups = validated_data.pop('groups')

            self.__set_groups(instance, groups)

        return super().update(instance, validated_data)

    def delete(self, instance, validated_data):
        pass

    def __set_groups(self, instance, groups):
        user_group_gene_panel = []
        for group in groups:
            user_group_gene_panel.append(UserGroupGenePanel(group=group, gene_panel=instance))

        instance.groups.clear()
        UserGroupGenePanel.objects.bulk_create(user_group_gene_panel)
