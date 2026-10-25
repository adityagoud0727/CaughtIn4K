import base64
import hashlib
import struct
from pathlib import Path

from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


MAGIC = b"C4K1"
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32


def derive_key(password, salt):
    """
    Derive a 256-bit encryption key from the password.
    """

    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
        dklen=KEY_SIZE
    )


def bytes_to_bits(data):
    """
    Convert bytes to individual bits.
    """

    bits = []

    for byte in data:

        for i in range(7, -1, -1):

            bits.append(
                (byte >> i) & 1
            )

    return bits


def bits_to_bytes(bits):
    """
    Convert individual bits back into bytes.
    """

    output = bytearray()

    for index in range(
        0,
        len(bits),
        8
    ):

        byte = 0

        for bit in bits[index:index + 8]:

            byte = (
                byte << 1
            ) | bit

        output.append(byte)

    return bytes(output)


def encrypt_message(message, password):
    """
    Encrypt a message using AES-256-GCM.
    """

    if not password:
        raise ValueError(
            "Password cannot be empty."
        )

    salt = __import__("secrets").token_bytes(
        SALT_SIZE
    )

    nonce = __import__("secrets").token_bytes(
        NONCE_SIZE
    )

    key = derive_key(
        password,
        salt
    )

    aes = AESGCM(key)

    encrypted = aes.encrypt(
        nonce,
        message.encode("utf-8"),
        None
    )

    return (
        MAGIC
        + salt
        + nonce
        + struct.pack(
            ">I",
            len(encrypted)
        )
        + encrypted
    )


def decrypt_message(payload, password):
    """
    Decrypt an embedded CaughtIn4K payload.
    """

    if len(payload) < 36:

        raise ValueError(
            "Invalid PixelVault payload."
        )

    if payload[:4] != MAGIC:

        raise ValueError(
            "This image does not contain "
            "a valid PixelVault payload."
        )

    salt = payload[4:20]

    nonce = payload[20:32]

    encrypted_length = struct.unpack(
        ">I",
        payload[32:36]
    )[0]

    encrypted = payload[
        36:36 + encrypted_length
    ]

    key = derive_key(
        password,
        salt
    )

    aes = AESGCM(key)

    try:

        decrypted = aes.decrypt(
            nonce,
            encrypted,
            None
        )

    except Exception:

        raise ValueError(
            "Incorrect password or corrupted data."
        )

    return decrypted.decode(
        "utf-8"
    )


def get_capacity(image):
    """
    Return the maximum payload capacity in bytes.
    """

    if image.mode not in (
        "RGB",
        "RGBA"
    ):

        image = image.convert(
            "RGB"
        )

    usable_channels = (
        image.width
        * image.height
        * len(image.getbands())
    )

    return max(
        0,
        usable_channels // 8
    )


def embed_payload(
    input_path,
    output_path,
    payload
):
    """
    Embed encrypted payload into image pixels.
    """

    input_path = Path(
        input_path
    )

    output_path = Path(
        output_path
    )

    if input_path.suffix.lower() != ".png":

        raise ValueError(
            "PixelVault currently supports PNG images only."
        )

    image = Image.open(
        input_path
    ).convert("RGB")

    pixels = list(
        image.getdata()
    )

    payload_length = len(
        payload
    )

    required_bytes = (
        4
        + payload_length
    )

    capacity = get_capacity(
        image
    )

    if required_bytes > capacity:

        image.close()

        raise ValueError(
            "Message is too large for this image.\n"
            f"Required: {required_bytes} bytes\n"
            f"Available: {capacity} bytes"
        )

    data = (
        struct.pack(
            ">I",
            payload_length
        )
        + payload
    )

    bits = bytes_to_bits(
        data
    )

    bit_index = 0

    modified_pixels = []

    for pixel in pixels:

        new_pixel = []

        for channel in pixel:

            value = channel

            if bit_index < len(bits):

                value = (
                    value & 0xFE
                ) | bits[bit_index]

                bit_index += 1

            new_pixel.append(
                value
            )

        modified_pixels.append(
            tuple(new_pixel)
        )

    clean_image = Image.new(
        "RGB",
        image.size
    )

    clean_image.putdata(
        modified_pixels
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    clean_image.save(
        output_path,
        "PNG"
    )

    clean_image.close()
    image.close()

    return str(
        output_path
    )


def extract_payload(
    image_path
):
    """
    Extract the embedded payload.
    """

    image = Image.open(
        image_path
    ).convert("RGB")

    pixels = list(
        image.getdata()
    )

    bits = []

    for pixel in pixels:

        for channel in pixel:

            bits.append(
                channel & 1
            )

    # First 32 bits contain payload length.
    if len(bits) < 32:

        image.close()

        raise ValueError(
            "Image is too small."
        )

    length_bytes = bits_to_bytes(
        bits[:32]
    )

    payload_length = struct.unpack(
        ">I",
        length_bytes
    )[0]

    required_bits = (
        32
        + payload_length * 8
    )

    if required_bits > len(bits):

        image.close()

        raise ValueError(
            "Invalid or corrupted PixelVault data."
        )

    payload_bits = bits[
        32:required_bits
    ]

    payload = bits_to_bytes(
        payload_bits
    )

    image.close()

    return payload


def hide_message(
    input_path,
    output_path,
    message,
    password
):
    """
    Encrypt and embed a message.
    """

    payload = encrypt_message(
        message,
        password
    )

    return embed_payload(
        input_path,
        output_path,
        payload
    )


def extract_message(
    image_path,
    password
):
    """
    Extract and decrypt a message.
    """

    payload = extract_payload(
        image_path
    )

    return decrypt_message(
        payload,
        password
    )


if __name__ == "__main__":

    print(
        "PixelVault core module loaded."
    )