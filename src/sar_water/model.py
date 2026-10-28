"""The locked compact VV/VH water segmenter and valid-pixel loss.

PyTorch is optional for the classical experiment. This model produces water
logits, not denoised SAR, so its outputs do not have ENL/PSNR interpretations.
"""
from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class _DoubleConv(nn.Sequential):
    def __init__(self, incoming, outgoing):
        super().__init__(
            nn.Conv2d(incoming, outgoing, 3, padding=1, bias=False),
            nn.GroupNorm(8, outgoing), nn.ReLU(),
            nn.Conv2d(outgoing, outgoing, 3, padding=1, bias=False),
            nn.GroupNorm(8, outgoing), nn.ReLU(),
        )


class CompactUNet(nn.Module):
    """487,857 parameters; three pools and bilinear skip-size upsampling."""

    def __init__(self):
        super().__init__()
        self.encoders = nn.ModuleList([_DoubleConv(2, 16), _DoubleConv(16, 32),
                                       _DoubleConv(32, 64), _DoubleConv(64, 128)])
        self.decoders = nn.ModuleList([_DoubleConv(192, 64), _DoubleConv(96, 32),
                                       _DoubleConv(48, 16)])
        self.head = nn.Conv2d(16, 1, 1)

    def forward(self, inputs):
        if inputs.ndim != 4 or inputs.shape[1] != 2 or min(inputs.shape[-2:]) < 8:
            raise ValueError('expected N,2,H,W input shape with spatial size >= 8')
        skips = []
        current = inputs
        for block in self.encoders[:-1]:
            current = block(current)
            skips.append(current)
            current = F.max_pool2d(current, 2)
        current = self.encoders[-1](current)
        for block, skip in zip(self.decoders, reversed(skips)):
            current = F.interpolate(current, size=skip.shape[-2:], mode='bilinear',
                                    align_corners=False)
            current = block(torch.cat((current, skip), dim=1))
        return self.head(current)


def masked_bce_dice_loss(logits, targets, valid):
    """Batch-pooled valid-pixel BCE/Dice; None means skip an empty batch.

    Index before computing either term: invalid labels can contain NaNs without
    poisoning a loss or its gradients. Nonfinite *scored* values are rejected.
    """
    if logits.shape != targets.shape or logits.shape != valid.shape:
        raise ValueError('logits, targets and validity shape mismatch')
    valid = valid.to(dtype=torch.bool)
    if not valid.any():
        return None
    selected, truth = logits[valid], targets[valid].to(dtype=logits.dtype)
    if not torch.isfinite(selected).all():
        raise ValueError('valid logits must be finite')
    if not torch.isfinite(truth).all() or not torch.all((truth == 0) | (truth == 1)):
        raise ValueError('valid labels must be finite binary values')
    bce = F.binary_cross_entropy_with_logits(selected, truth, reduction='mean')
    probabilities = torch.sigmoid(selected)
    dice = 1 - (2 * (probabilities * truth).sum() + 1e-6) / (
        probabilities.sum() + truth.sum() + 1e-6)
    return .5 * bce + .5 * dice
