import strawberry

from user.graphql.mutations import KeainUserMutation
from user.graphql.queries import KeainUserQuery


@strawberry.type
class Query(KeainUserQuery):
    pass


@strawberry.type
class Mutation(KeainUserMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
