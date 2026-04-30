import strawberry
from graphql import GraphQLError
from strawberry.file_uploads import Upload
from strawberry.types.info import Info

from analyzer.graphql.types import AnalyzeResult
from analyzer.services import analyze_keyboard_audio
from core.permissions import IsAuthenticated


@strawberry.type
class AnalyzerMutation:
    @strawberry.mutation(
        description=(
            "Analyze up to 10s of keyboard typing-test audio (mobile-mic friendly) "
            "and return acoustic scores. Free tier uses librosa DSP only."
        ),
        permission_classes=[IsAuthenticated],
    )
    def analyze_file(self, info: Info, file: Upload) -> AnalyzeResult:
        try:
            result = analyze_keyboard_audio(file)
            print(result)
            return result
        except GraphQLError:
            raise
        except ValueError as e:
            raise GraphQLError(
                str(e),
                extensions={"code": "INVALID_AUDIO", "reason": "INPUT"},
            ) from e
        except Exception as e:
            raise GraphQLError(
                f"Failed to analyze audio: {e}",
                extensions={"code": "INTERNAL"},
            ) from e
