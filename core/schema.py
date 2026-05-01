import strawberry
from django.core.files.uploadedfile import UploadedFile
from strawberry.file_uploads import UploadDefinition

from analyzer.graphql.mutations import AnalyzerMutation
from build.graphql.mutations import BuildMutation
from build.graphql.queries import BuildQuery
from user.graphql.mutations import KeainUserMutation
from user.graphql.queries import KeainUserQuery


@strawberry.type
class Query(KeainUserQuery, BuildQuery):
    pass


@strawberry.type
class Mutation(KeainUserMutation, AnalyzerMutation, BuildMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    scalar_overrides={UploadedFile: UploadDefinition},
)
