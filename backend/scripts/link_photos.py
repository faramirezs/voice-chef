import os
import re
import unicodedata
import uuid
import shutil
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.utils.file_service_image_utils import delete_file

DATABASE_URL = settings.DATABASE_URL

SRC_DIR = "/assets/recipe_seed_images"
UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_URL_PREFIX = settings.UPLOAD_URL_PREFIX


def slugify(name: str) -> str:
    # normalize unicode (ä → a, etc.)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()

    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)  # replace non-alphanum with dash
    name = name.strip("-")

    return name


def link_images_to_db():
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        recipes = conn.execute(text("""
            SELECT id, LOWER(name) AS name,
            photo_url
            FROM recipes
        """)).fetchall()

        for recipe_id, name, photo_url in recipes:

            # Skip if the file already exists on disk (user-uploaded or previously seeded)
            if photo_url:
                filename = os.path.basename(photo_url)
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    continue

            slug = slugify(name)
            filename_guess = f"{slug}.jpg"

            src_path = os.path.join(SRC_DIR, filename_guess)
            
            if not os.path.exists(src_path):
                continue

            # Delete old photo reference from DB if it exists but file is gone
            if photo_url:
                delete_file(photo_url)

            file_uuid = str(uuid.uuid4())
            filename = f"{file_uuid}.jpg"

            dst_path = os.path.join(UPLOAD_DIR, filename)
            
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            shutil.copyfile(src_path, dst_path)

            photo_url = f"{UPLOAD_URL_PREFIX}/{filename}"

            conn.execute(
                text("""
                    UPDATE recipes
                    SET photo_url = :photo_url
                    WHERE id = :id
                """),
                {"photo_url": photo_url, "id": recipe_id},
            )

    print("Seed images linked.")


def main():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")

    link_images_to_db()


if __name__ == "__main__":
    main()