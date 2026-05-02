from typing import Optional

import strawberry
from graphql import GraphQLError
from strawberry.file_uploads import Upload
from strawberry.types.info import Info

from analyzer.graphql.types import AnalyzeResult
from analyzer.models import Analysis
from analyzer.services import analyze_keyboard_audio
from build.models import Build
from core.error_codes import INTERNAL, INVALID_AUDIO, NOT_FOUND, err
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
    def analyze_file(
        self, info: Info, file: Upload, build_id: Optional[strawberry.ID]
    ) -> AnalyzeResult:
        build = None
        try:
            if build_id:
                build = Build.objects.get(id=build_id)
        except Build.DoesNotExist:
            raise GraphQLError("Build not found", extensions=err(NOT_FOUND))
        try:
            result = analyze_keyboard_audio(file)
            file.seek(0)
            Analysis.objects.create(
                **strawberry.asdict(result), owner=info.context["user"], audio=file, build=build
            )

            return result
        except GraphQLError:
            raise
        except ValueError as e:
            raise GraphQLError(
                str(e),
                extensions=err(INVALID_AUDIO, reason="INPUT"),
            ) from e
        except Exception as e:
            raise GraphQLError(
                f"Failed to analyze audio: {e}",
                extensions=err(INTERNAL),
            ) from e
