import strawberry
from graphql import GraphQLError
from strawberry.file_uploads import Upload
from strawberry.types.info import Info

from core.permissions import IsAuthenticated


@strawberry.type
class AnalyzerMutation:
    @strawberry.mutation(
        description="Analyze a file and return the results", permission_classes=[IsAuthenticated]
    )
    def analyze_file(self, info: Info, file: Upload) -> str:
        # Placeholder for actual analysis logic
        return f"File '{file}' analyzed successfully"
