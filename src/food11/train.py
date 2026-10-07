import argparse

import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

CLASSES = [
    "Bread", "Dairy product", "Dessert", "Egg", "Fried food", "Meat",
    "Noodles-Pasta", "Rice", "Seafood", "Soup", "Vegetable-Fruit",
]

TRANSFORM = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def get_dataloaders(dataset_name, batch_size):
    base = "data/food11_processed" if dataset_name == "processed" else "data/food11_processed_mini"

    train_ds = datasets.ImageFolder(f"{base}/training", transform=TRANSFORM)
    val_ds = datasets.ImageFolder(f"{base}/validation", transform=TRANSFORM)
    test_ds = datasets.ImageFolder(f"{base}/evaluation", transform=TRANSFORM)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loader


def build_model(num_classes=11):
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total


def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_loader, val_loader, test_loader = get_dataloaders(args.dataset, args.batch_size)

    model = build_model(num_classes=len(CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("food11")

    with mlflow.start_run():
        mlflow.log_params({
            "dataset": args.dataset,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": args.batch_size,
            "model": "resnet18",
        })

        for epoch in range(args.epochs):
            model.train()
            running_loss, seen = 0.0, 0
            for images, labels in train_loader:
                images, labels = images.to(device), labels.to(device)

                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item() * images.size(0)
                seen += images.size(0)

            train_loss = running_loss / seen
            val_loss, val_accuracy = evaluate(model, val_loader, criterion, device)

            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss", val_loss, step=epoch)
            mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)

            print(f"Epoch {epoch + 1}/{args.epochs} - train_loss: {train_loss:.4f} "
                  f"- val_loss: {val_loss:.4f} - val_accuracy: {val_accuracy:.4f}")

        test_loss, test_accuracy = evaluate(model, test_loader, criterion, device)
        mlflow.log_metric("test_accuracy", test_accuracy)
        print(f"Final test_accuracy: {test_accuracy:.4f}")

        example_images, _ = next(iter(train_loader))
        input_example = example_images[:1].numpy()
        mlflow.pytorch.log_model(model, "model", input_example=input_example)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["processed", "mini"], default="mini")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())