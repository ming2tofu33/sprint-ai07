import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database import get_connection
from app.sentiment import analyze_sentiment, get_model_name


def main() -> None:
    with get_connection() as connection:
        rows = connection.execute("SELECT id, content FROM reviews ORDER BY id").fetchall()
        for row in rows:
            result = analyze_sentiment(row["content"])
            connection.execute(
                """
                UPDATE reviews
                SET sentiment_label = ?,
                    sentiment_score = ?,
                    sentiment_confidence = ?
                WHERE id = ?
                """,
                (
                    result.sentiment_label,
                    result.sentiment_score,
                    result.confidence,
                    row["id"],
                ),
            )
            print(
                f"review_id={row['id']} label={result.sentiment_label} "
                f"score={result.sentiment_score} confidence={result.confidence}"
            )

    print(f"recomputed {len(rows)} reviews with {get_model_name()}")


if __name__ == "__main__":
    main()
