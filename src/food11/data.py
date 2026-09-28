from pathlib import Path
from PIL import Image

# The 11 categories, in order (the number in the file name is the index)
CLASSES = [
    "Bread", "Dairy product", "Dessert", "Egg", "Fried food", "Meat",
    "Noodles-Pasta", "Rice", "Seafood", "Soup", "Vegetable-Fruit",
]

SPLITS = ["training", "evaluation", "validation"]
SIZE = (128, 128)
MINI_MAX_PER_CLASS = 100

DATA = Path("data")
RAW = DATA / "food11_raw"
PROCESSED = DATA / "food11_processed"
MINI = DATA / "food11_processed_mini"


def main():
    for split in SPLITS:
        mini_counts = {name: 0 for name in CLASSES}

        for img_path in sorted((RAW / split).glob("*.jpg")):
            # File name looks like "0_123.jpg": first part is the category number
            class_id = int(img_path.stem.split("_")[0])
            class_name = CLASSES[class_id]

            # Open, convert to RGB, shrink to 128x128
            img = Image.open(img_path).convert("RGB").resize(SIZE)

            # Save in the full processed dataset
            out_dir = PROCESSED / split / class_name
            out_dir.mkdir(parents=True, exist_ok=True)
            img.save(out_dir / img_path.name)

            # Also save in the mini dataset, up to 100 per category
            if mini_counts[class_name] < MINI_MAX_PER_CLASS:
                mini_dir = MINI / split / class_name
                mini_dir.mkdir(parents=True, exist_ok=True)
                img.save(mini_dir / img_path.name)
                mini_counts[class_name] += 1

        print(f"Done: {split}")


if __name__ == "__main__":
    main()





