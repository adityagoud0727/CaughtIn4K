from pathlib import Path
import shutil

from PIL import Image


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def sanitize_image(input_path, output_path):
    """
    Remove image metadata and save a cleaned copy.

    The original file is never modified.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(
            f"File not found: {input_path}"
        )

    extension = input_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported image format. "
            "Supported formats: JPG, JPEG and PNG."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with Image.open(input_path) as image:

        # Copy only the actual pixel data.
        # This intentionally avoids carrying EXIF/info metadata.
        clean_image = Image.new(
            image.mode,
            image.size
        )

        clean_image.putdata(
            list(image.getdata())
        )

        if extension in {".jpg", ".jpeg"}:

            # JPEG does not support RGBA.
            if clean_image.mode not in ("RGB", "L", "CMYK"):
                clean_image = clean_image.convert("RGB")

            clean_image.save(
                output_path,
                format="JPEG",
                quality=95,
                optimize=True
            )

        else:

            # PNG can preserve transparency through RGBA.
            clean_image.save(
                output_path,
                format="PNG",
                optimize=True
            )

        clean_image.close()

    return str(output_path)


def sanitize_file(input_path):
    """
    Automatically create a cleaned filename beside the original.

    Example:
        photo.jpg
        ↓
        photo_CLEANED.jpg
    """

    input_path = Path(input_path)

    output_path = (
        input_path.parent
        / f"{input_path.stem}_CLEANED{input_path.suffix}"
    )

    return sanitize_image(
        input_path,
        output_path
    )


if __name__ == "__main__":

    file_path = input(
        "Enter image path: "
    ).strip().strip('"')

    try:

        cleaned = sanitize_file(
            file_path
        )

        print(
            "\nSanitization completed successfully."
        )

        print(
            f"Cleaned file:\n{cleaned}"
        )

    except Exception as error:

        print(
            f"\nSanitization failed: {error}"
        )