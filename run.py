"""Compute depth maps for images in the input folder.
"""
import os
import glob
import torch
from monodepth_net import MonoDepthNet
import MiDaS_utils as utils
import numpy as np
import cv2



def run_depth():
    """Run MonoDepthNN to compute depth maps.

    Args:
        input_path (str): path to input folder
        output_path (str): path to output folder
        model_path (str): path to saved model
    """
    # set paths
    input_path = os.path.join(os.getcwd(), 'input' + os.sep)
    output_path = os.path.join(os.getcwd(), 'output' + os.sep)
    model_path = os.path.join(os.getcwd(), 'model.pt' + os.sep)
    target_w = None
    print("initialize")

    # select device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device: %s" % device)

    # load network
    model = MonoDepthNet(model_path)
    model.to(device)
    model.eval()

    # get input
    img_names = glob.glob(os.path.join(input_path, "*"))
    num_images = len(img_names)

    # create output folder
    os.makedirs(output_path, exist_ok=True)

    print("start processing")

    for ind, img_name in enumerate(img_names):
        print("  processing {} ({}/{})".format(img_name, ind + 1, num_images))

        # input
        img = utils.read_image(img_name)
        w = img.shape[1]
        scale = 640. / max(img.shape[0], img.shape[1])
        target_height, target_width = int(round(img.shape[0] * scale)), int(round(img.shape[1] * scale))
        img_input = utils.resize_image(img)
        print(img_input.shape)
        img_input = img_input.to(device)
        # compute
        with torch.no_grad():
            out = model.forward(img_input)

        depth = utils.resize_depth(out, target_width, target_height)
        img = cv2.resize((img * 255).astype(np.uint8), (target_width, target_height), interpolation=cv2.INTER_AREA)

        filename = os.path.join(
            output_path, os.path.splitext(os.path.basename(img_name))[0]
        )
        # np.save(filename + '.npy', depth)
        utils.write_depth(filename, depth, bits=2)

    print("finished")


if __name__ == "__main__":
    # set torch options
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True

    # compute depth maps
    run_depth()
