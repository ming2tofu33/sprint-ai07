from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "미션18_4팀_김도민_보고서.pdf"
SCREENSHOT_DIR = BASE_DIR / "screenshots"
FONT_REGULAR = r"C:\Windows\Fonts\malgun.ttf"
FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"


def register_fonts() -> tuple[str, str]:
    pdfmetrics.registerFont(TTFont("Malgun", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("MalgunBold", FONT_BOLD))
    return "Malgun", "MalgunBold"


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("\n", "<br/>"), style)


def add_section(story: list, title: str, body: str, styles: dict) -> None:
    story.append(Paragraph(title, styles["h2"]))
    story.append(paragraph(body, styles["body"]))
    story.append(Spacer(1, 0.35 * cm))


def add_table(story: list, rows: list[list[str]], widths: list[float], styles: dict) -> None:
    table_data = [[paragraph(cell, styles["table_head"]) for cell in rows[0]]]
    for row in rows[1:]:
        table_data.append([paragraph(cell, styles["table_cell"]) for cell in row])
    table = Table(table_data, colWidths=widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.4 * cm))


def add_image(story: list, filename: str, caption: str, styles: dict, width_cm: float = 16.5) -> None:
    path = SCREENSHOT_DIR / filename
    if not path.exists():
        return
    image = Image(str(path))
    max_width = width_cm * cm
    ratio = max_width / image.imageWidth
    image.drawWidth = max_width
    image.drawHeight = image.imageHeight * ratio
    story.append(KeepTogether([Paragraph(caption, styles["caption"]), Spacer(1, 0.15 * cm), image]))
    story.append(Spacer(1, 0.45 * cm))


def build() -> None:
    font, bold_font = register_fonts()
    base_styles = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "TitleKo",
            parent=base_styles["Title"],
            fontName=bold_font,
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h2": ParagraphStyle(
            "HeadingKo",
            parent=base_styles["Heading2"],
            fontName=bold_font,
            fontSize=14,
            leading=19,
            textColor=colors.HexColor("#111827"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyKo",
            parent=base_styles["BodyText"],
            fontName=font,
            fontSize=9.5,
            leading=15,
            textColor=colors.HexColor("#1F2937"),
        ),
        "caption": ParagraphStyle(
            "CaptionKo",
            parent=base_styles["BodyText"],
            fontName=bold_font,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        ),
        "table_head": ParagraphStyle(
            "TableHeadKo",
            parent=base_styles["BodyText"],
            fontName=bold_font,
            fontSize=8.3,
            leading=11,
        ),
        "table_cell": ParagraphStyle(
            "TableCellKo",
            parent=base_styles["BodyText"],
            fontName=font,
            fontSize=8.1,
            leading=10.5,
        ),
    }

    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.3 * cm,
        title="미션18_4팀_김도민_보고서",
    )

    story = [Paragraph("미션 18 보고서", styles["title"])]
    add_section(
        story,
        "1. 서비스 개요",
        "한국 영화 정보, 사용자 리뷰, 리뷰 감성 분석 결과를 표시하는 웹 애플리케이션이다. "
        "프론트엔드는 Streamlit, 백엔드는 FastAPI로 구현했다. 사용자는 영화 목록을 확인하고, "
        "영화를 등록하고, 특정 영화에 리뷰를 작성할 수 있다. 리뷰 등록 시 백엔드에서 감성 분석을 수행하고 "
        "결과를 리뷰와 함께 저장한다.",
        styles,
    )
    add_table(
        story,
        [
            ["구분", "기술"],
            ["프론트엔드", "Streamlit"],
            ["백엔드", "FastAPI"],
            ["데이터베이스", "SQLite"],
            ["데이터 검증", "Pydantic"],
            ["테스트", "pytest, FastAPI TestClient"],
            ["감성 분석", "Hugging Face cringepnh/koelectra-korean-sentiment"],
        ],
        [4 * cm, 12 * cm],
        styles,
    )
    add_section(
        story,
        "2. 서비스 구조도",
        "사용자 -> Streamlit 프론트엔드 -> FastAPI 백엔드 -> SQLite 데이터베이스 구조로 동작한다. "
        "리뷰 등록 요청이 들어오면 FastAPI가 Hugging Face 감성 분석 모델을 호출하고, 감성 label과 score를 리뷰와 함께 저장한다. "
        "Streamlit은 데이터를 직접 저장하지 않고 FastAPI API만 호출한다.",
        styles,
    )
    add_section(
        story,
        "3. 데이터베이스 ERD",
        "movies 테이블은 영화의 기본 정보와 포스터 URL을 저장한다. reviews 테이블은 movie_id 외래키를 통해 "
        "영화에 연결되며, 작성자, 리뷰 내용, 감성 분석 결과를 저장한다. 영화 1개는 여러 리뷰를 가질 수 있는 1:N 구조이다.",
        styles,
    )
    add_table(
        story,
        [
            ["테이블", "주요 필드", "설명"],
            ["movies", "id, title, release_date, director, genre, poster_url, created_at, updated_at", "영화 기본 정보"],
            ["reviews", "id, movie_id, author_name, content, sentiment_label, sentiment_score, sentiment_confidence, created_at", "리뷰와 감성 분석 결과"],
        ],
        [3 * cm, 8.5 * cm, 4.5 * cm],
        styles,
    )
    add_section(
        story,
        "4. 주요 API",
        "GET /health, POST /movies, GET /movies, GET /movies/{movie_id}, DELETE /movies/{movie_id}, "
        "POST /movies/{movie_id}/reviews, GET /movies/{movie_id}/reviews, GET /reviews, "
        "DELETE /reviews/{review_id}, GET /movies/{movie_id}/rating, POST /sentiment/analyze 를 구현했다.",
        styles,
    )
    add_section(
        story,
        "5. 감성 분석 방식",
        "현재 버전은 Hugging Face의 cringepnh/koelectra-korean-sentiment 모델을 사용한다. "
        "이 모델은 한국어 영화 리뷰 데이터셋인 NSMC 기반 KoELECTRA 계열 감성 분석 모델이다. "
        "모델 출력이 긍정이면 confidence를 sentiment_score로 저장하고, 부정이면 1 - confidence를 저장한다. "
        "결과는 sentiment_label, sentiment_score, sentiment_confidence로 저장한다.",
        styles,
    )
    add_table(
        story,
        [
            ["영화", "감독", "리뷰 수", "평균 감성 점수"],
            ["파묘", "장재현", "10", "97.2점"],
            ["서울의 봄", "김성수", "10", "98.7점"],
            ["기생충", "봉준호", "10", "99.4점"],
        ],
        [4 * cm, 4 * cm, 3 * cm, 5 * cm],
        styles,
    )
    story.append(PageBreak())
    add_image(story, "fastapi_docs.png", "FastAPI Docs 전체 캡처", styles)
    add_image(story, "streamlit_movie_list.png", "Streamlit 영화 목록 화면", styles)
    add_image(story, "streamlit_review_management.png", "Streamlit 리뷰 관리 화면", styles)
    add_section(
        story,
        "6. 테스트 결과",
        "백엔드 테스트: python -m pytest tests/test_api.py -q -> 3 passed\n"
        "프론트엔드 API 클라이언트 테스트: python -m pytest tests/test_api_client.py -q -> 3 passed\n"
        "로컬 실행 확인: backend /health 200, movies 3개, frontend 200",
        styles,
    )
    add_section(
        story,
        "7. 문제 해결 과정",
        "Streamlit이 직접 데이터를 저장하지 않도록 API 클라이언트를 분리했다. 제출 캡처용 데이터는 시드 스크립트로 자동 등록하게 만들었다. "
        "초기 규칙 기반 감성 분석기는 Hugging Face 한국어 감성 분석 모델로 교체했고, 기존 리뷰는 재계산 스크립트로 다시 분석했다. "
        "초기 placeholder 포스터는 TMDB 실제 포스터 이미지 URL로 교체했다. Streamlit 컴포넌트를 HTML div로 감쌌을 때 빈 박스가 생겨 "
        "st.container(border=True) 기반 카드 구조로 수정했다.",
        styles,
    )
    add_section(
        story,
        "8. 참고 자료",
        "TMDB Exhuma poster page: https://www.themoviedb.org/movie/838209/images/posters?language=ko-KR\n"
        "TMDB 12.12: The Day poster page: https://www.themoviedb.org/movie/919207/images/posters\n"
        "TMDB Parasite poster page: https://www.themoviedb.org/movie/496243/images/posters?language=en-US\n"
        "Hugging Face model: https://huggingface.co/cringepnh/koelectra-korean-sentiment",
        styles,
    )

    doc.build(story)


if __name__ == "__main__":
    build()
