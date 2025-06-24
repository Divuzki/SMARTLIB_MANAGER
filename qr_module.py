# qr_module.py
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def generate_qr(data, output_file="qr.png"):
    """
    Generate a QR code with the given data and save it to the specified file.
    
    Args:
        data (str): The data to encode in the QR code
        output_file (str): The path where the QR code image will be saved
    
    Returns:
        str: The path to the saved QR code file
    
    Raises:
        Exception: If there's an error generating or saving the QR code
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Create QR code instance with better settings
        qr = qrcode.QRCode(
            version=1,  # Controls the size of the QR Code
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # About 7% or less errors can be corrected
            box_size=10,  # Controls how many pixels each "box" of the QR code is
            border=4,  # Controls how many boxes thick the border should be
        )
        
        # Add data and optimize
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image with better quality
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to RGB if needed (for better compatibility)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save the image
        img.save(output_file, quality=95, optimize=True)
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Error generating QR code: {str(e)}")

def generate_qr_with_logo(data, output_file="qr_with_logo.png", logo_path=None):
    """
    Generate a QR code with an optional logo in the center.
    
    Args:
        data (str): The data to encode in the QR code
        output_file (str): The path where the QR code image will be saved
        logo_path (str): Optional path to a logo image to embed in the center
    
    Returns:
        str: The path to the saved QR code file
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Create QR code with higher error correction for logo embedding
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create the QR code image
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        # Add logo if provided and exists
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                
                # Calculate logo size (should be about 1/5 of QR code size)
                qr_width, qr_height = img.size
                logo_size = min(qr_width, qr_height) // 5
                
                # Resize logo
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Calculate position to center the logo
                logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                
                # Paste logo onto QR code
                img.paste(logo, logo_pos)
                
            except Exception as logo_error:
                print(f"Warning: Could not add logo - {str(logo_error)}")
        
        # Save the image
        img.save(output_file, quality=95, optimize=True)
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Error generating QR code with logo: {str(e)}")

def create_qr_with_text(data, output_file="qr_with_text.png", title="QR Code"):
    """
    Generate a QR code with descriptive text below it.
    
    Args:
        data (str): The data to encode in the QR code
        output_file (str): The path where the QR code image will be saved
        title (str): Title text to display below the QR code
    
    Returns:
        str: The path to the saved QR code file
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Generate basic QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create the QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        # Create a new image with space for text
        qr_width, qr_height = qr_img.size
        text_height = 60  # Space for text
        
        final_img = Image.new('RGB', (qr_width, qr_height + text_height), 'white')
        
        # Paste QR code
        final_img.paste(qr_img, (0, 0))
        
        # Add text
        draw = ImageDraw.Draw(final_img)
        
        try:
            # Try to use a better font if available
            font = ImageFont.truetype("Arial.ttf", 16)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        text_bbox = draw.textbbox((0, 0), title, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (qr_width - text_width) // 2
        text_y = qr_height + 20
        
        # Draw the text
        draw.text((text_x, text_y), title, fill="black", font=font)
        
        # Save the final image
        final_img.save(output_file, quality=95, optimize=True)
        
        return output_file
        
    except Exception as e:
        raise Exception(f"Error generating QR code with text: {str(e)}")

def validate_qr_data(data):
    """
    Validate that the data can be encoded in a QR code.
    
    Args:
        data (str): The data to validate
    
    Returns:
        bool: True if data is valid, False otherwise
    """
    try:
        if not data or len(data.strip()) == 0:
            return False
        
        # Check if data is too long (QR codes have limits)
        if len(data) > 2953:  # Approximate limit for alphanumeric data
            return False
        
        # Try to create a QR code to validate
        qr = qrcode.QRCode()
        qr.add_data(data)
        qr.make(fit=True)
        
        return True
        
    except Exception:
        return False
