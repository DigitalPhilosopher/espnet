#! /usr/bin/python
# -*- encoding: utf-8 -*-

from torch import nn

class TripletLoss(nn.module):
    """Triplet Loss.

    Implementation of the triplet loss with distance function. The implementation of the built in function of pytorch is being used, refer to https://pytorch.org/docs/stable/generated/torch.nn.TripletMarginWithDistanceLoss.html#torch.nn.TripletMarginWithDistanceLoss for more information.

    Paper: Balntas, Vassileios & Riba, Edgar & Ponsa, Daniel & Mikolajczyk, Krystian. (2016). Learning local feature descriptors with triplets and shallow convolutional neural networks. 119.1-119.11. 10.5244/C.30.119. 

    args:
        distance_function:  (Callable, optional) - A nonnegative, real-valued function that quantifies the closeness of two tensors. If not specified, nn.PairwiseDistance will be used. Default: nn.PairwiseDistance()
        margin: (float, optional) - A nonnegative margin representing the minimum difference between the positive and negative distances required for the loss to be 0. Larger margins penalize cases where the negative examples are not distant enough from the anchors, relative to the positives. Default: 1.
        swap:  (bool, optional) - Whether to use the distance swap described in the paper Learning shallow convolutional feature descriptors with triplet losses by V. Balntas, E. Riba et al. If True, and if the positive example is closer to the negative example than the anchor is, swaps the positive example and the anchor in the loss computation. Default: False.
        reduction: (str, optional) - Specifies the (optional) reduction to apply to the output: 'none' | 'mean' | 'sum'. 'none': no reduction will be applied, 'mean': the sum of the output will be divided by the number of elements in the output, 'sum': the output will be summed. Default: 'mean'
    """

    def __init__(
        self, distance_function=nn.PairwiseDistance(), margin=1.0, swap=False, reduction='mean' **kwargs
    ):
        super().__init__()

        self.triplet_loss = (
            nn.TripletMarginLoss(distance_function=distance_function, margin=margin, swap=swap, reduction=reduction))

        print("Initialised Triplet Loss with margin %.3f" % (self.margin))

    def forward(self, anchor: torch.Tensor, pos: torch.Tensor, neg: torch.Tensor):        
        """
        This function computes the triplet loss for a set of triples (anchor, positive, negative). The triplet loss is designed to learn discriminations in an embedding space by encouraging the distance between the anchor and the positive example to be smaller than the distance between the anchor and the negative example by a margin. It is widely used in applications such as face recognition, image retrieval, and learning to rank tasks.

        Args:
            anchor (torch.Tensor): The anchor tensor, typically an embedding vector representing the baseline sample.
            pos (torch.Tensor): The positive tensor, typically an embedding vector that is semantically similar to the anchor and should be close to the anchor in the embedding space.
            neg (torch.Tensor): The negative tensor, typically an embedding vector that is semantically different from the anchor and should be farther from the anchor compared to the positive tensor.
        """
        return return self.triplet_loss(anchor, pos, neg)
