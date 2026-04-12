"""Image encoders for captioning models.

Three encoder variants:
- CNNEncoderGlobal: ResNet-50 backbone → global average pool → (B, embed_dim)
- CNNEncoderSpatial: ResNet-50 backbone → spatial feature map → (B, 49, embed_dim)
- ViTEncoder: ViT-B/16 backbone → patch tokens → (B, 196, embed_dim)
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torchvision.models as tv_models
import timm


class CNNEncoderGlobal(nn.Module):
    """ResNet-50 encoder that produces a single global feature vector per image.

    Args:
        embed_dim: Dimensionality of the output embedding.
        frozen: If True, all backbone parameters are frozen.
    """

    def __init__(self, embed_dim: int = 512, frozen: bool = True) -> None:
        super().__init__()

        resnet = tv_models.resnet50(weights=tv_models.ResNet50_Weights.IMAGENET1K_V1)
        # Keep all layers except the final fc
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])  # → (B, 2048, 1, 1)

        if frozen:
            for param in self.backbone.parameters():
                param.requires_grad = False

        self.proj = nn.Linear(2048, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 3, 224, 224)

        Returns:
            (B, embed_dim)
        """
        features = self.backbone(x)          # (B, 2048, 1, 1)
        features = features.flatten(1)       # (B, 2048)
        return self.proj(features)           # (B, embed_dim)


class CNNEncoderSpatial(nn.Module):
    """ResNet-50 encoder that produces a spatial grid of feature vectors.

    Args:
        embed_dim: Dimensionality of the output embedding per spatial location.
        frozen: If True, all backbone parameters are frozen.
    """

    def __init__(self, embed_dim: int = 512, frozen: bool = True) -> None:
        super().__init__()

        resnet = tv_models.resnet50(weights=tv_models.ResNet50_Weights.IMAGENET1K_V1)
        # Keep up to (and including) layer4, dropping avgpool and fc
        self.backbone = nn.Sequential(*list(resnet.children())[:-2])  # → (B, 2048, 7, 7)

        if frozen:
            for param in self.backbone.parameters():
                param.requires_grad = False

        self.proj = nn.Linear(2048, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 3, 224, 224)

        Returns:
            (B, 49, embed_dim)
        """
        features = self.backbone(x)                    # (B, 2048, 7, 7)
        B, C, H, W = features.shape
        features = features.permute(0, 2, 3, 1)        # (B, 7, 7, 2048)
        features = features.reshape(B, H * W, C)       # (B, 49, 2048)
        return self.proj(features)                     # (B, 49, embed_dim)


class ViTEncoder(nn.Module):
    """ViT-B/16 encoder that produces patch-level feature vectors.

    Args:
        embed_dim: Dimensionality of the output embedding per patch.
        frozen: If True, the entire ViT is frozen first.
        trainable_layers: Number of transformer blocks (from the end) to unfreeze
            when frozen=True.
    """

    def __init__(
        self,
        embed_dim: int = 512,
        frozen: bool = True,
        trainable_layers: int = 4,
    ) -> None:
        super().__init__()

        self.vit = timm.create_model(
            "vit_base_patch16_224",
            pretrained=True,
            num_classes=0,
        )

        if frozen:
            # Freeze everything first
            for param in self.vit.parameters():
                param.requires_grad = False

            # Unfreeze the last `trainable_layers` transformer blocks
            blocks = list(self.vit.blocks)
            for block in blocks[-trainable_layers:]:
                for param in block.parameters():
                    param.requires_grad = True

            # Unfreeze final norm layer
            for param in self.vit.norm.parameters():
                param.requires_grad = True

        self.proj = nn.Linear(768, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 3, 224, 224)

        Returns:
            (B, 196, embed_dim)
        """
        tokens = self.vit.forward_features(x)   # (B, 197, 768)
        patch_tokens = tokens[:, 1:, :]         # (B, 196, 768) — discard CLS token
        return self.proj(patch_tokens)          # (B, 196, embed_dim)
