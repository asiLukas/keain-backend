import strawberry
from django.core.files.uploadedfile import UploadedFile
from strawberry.file_uploads import UploadDefinition

from analyzer.graphql.mutations import AnalyzerMutation
from user.graphql.mutations import KeainUserMutation
from user.graphql.queries import KeainUserQuery


@strawberry.type
class Query(KeainUserQuery):
    pass


@strawberry.type
class Mutation(KeainUserMutation, AnalyzerMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    scalar_overrides={UploadedFile: UploadDefinition},
)
