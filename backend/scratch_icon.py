from PIL import Image
import os

source_path = r"C:\Users\karti\.gemini\antigravity-ide\brain\1aac546d-e380-471e-871b-6da6cad6f191\carbon_engine_logo_1780938129500.png"
public_dir = r"c:\Prompt Wars\challenge 3\frontend\public"

# Open the generated image
img = Image.open(source_path).convert("RGBA")

# Ensure the output directory exists
os.makedirs(public_dir, exist_ok=True)

# 1. Favicon (.ico)
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
img.save(os.path.join(public_dir, "favicon.ico"), format="ICO", sizes=icon_sizes)

# 2. Apple Touch Icon (180x180)
apple = img.resize((180, 180), Image.Resampling.LANCZOS)
apple.save(os.path.join(public_dir, "apple-touch-icon.png"), format="PNG")

# 3. PWA Icons
pwa192 = img.resize((192, 192), Image.Resampling.LANCZOS)
pwa192.save(os.path.join(public_dir, "pwa-192x192.png"), format="PNG")

pwa512 = img.resize((512, 512), Image.Resampling.LANCZOS)
pwa512.save(os.path.join(public_dir, "pwa-512x512.png"), format="PNG")

print("Successfully generated and replaced all logo assets in the frontend/public directory!")
