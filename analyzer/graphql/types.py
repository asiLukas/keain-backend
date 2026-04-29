import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class AnalyzeInput:
    file: Upload
