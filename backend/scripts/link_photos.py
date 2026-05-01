import os
import re
from sqlalchemy import create_engine, text
from photo_script import slugify

DATABASE_URL = os.getenv("DATABASE_URL")

SRC_DIR = "/assets/recipe_seed_images"
DST_DIR = "/code/uploads"
BASE_URL = "/uploads"


# def slugify(name: str) -> str:
#     name = name.lower()
#     name = re.sub(r"[^a-z0-9]+", "-", name)
#     return name.strip("-")


def copy_seed_images():
    if not os.path.exists(SRC_DIR):
        print("⚠️ No seed images directory found")
        return

    os.makedirs(DST_DIR, exist_ok=True)

    for filename in os.listdir(SRC_DIR):
        src = os.path.join(SRC_DIR, filename)
        dst = os.path.join(DST_DIR, filename)

        if not os.path.exists(dst):
            with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                fdst.write(fsrc.read())
            print(f"📦 Copied: {filename}")


def link_images_to_db():
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        recipes = conn.execute(
            text("SELECT id, name FROM recipes")
        ).fetchall()

        for recipe_id, name in recipes:
            slug = slugify(name)
            filename = f"{slug}.jpg"

            filepath = os.path.join(DST_DIR, filename)

            if not os.path.exists(filepath):
                print(f"❌ Missing image for: {name}")
                continue

            photo_url = f"{BASE_URL}/{filename}"

            conn.execute(
                text("""
                    UPDATE recipes
                    SET photo_url = :photo_url
                    WHERE id = :id
                      AND (photo_url IS NULL OR photo_url = '')
                """),
                {"photo_url": photo_url, "id": recipe_id},
            )

            print(f"✅ Linked: {name} → {photo_url}")
    print("Seed images are linked to recipes in the database.")


def main():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")

    copy_seed_images()
    link_images_to_db()


if __name__ == "__main__":
    main()