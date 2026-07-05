"""dlinso 기능 모듈 — 랜딩·라우팅 메타.

패키지 초기화 시 하위 모듈을 eager import 하지 않습니다(순환 import·Cloud 부팅 오류 방지).
호출부는 ``modules.home_registry`` 등을 직접 import 하세요.
"""

__all__: list[str] = []
