#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 08:34:53 2021

@author: marina
"""

import os
import numpy as np
from functions import read_image, reshape_image, extract_scales, ponomarenko, ponomarenko_blocks, read_estim, makeSameXrange
from skimage import io
import traceback
import argparse
import subprocess
import scipy.interpolate as interpolate


def do_one_image(f):
    k = [256, 128, 64] # size macroblock
    s = 0.5 # stride
    num_scales = 3 # number of scales
    g_i = 5 # filter iterations (ponomarenko) for the global image 
    g_b = 0 # filter iterations (ponomarenko )for the blocks 
    bins_macroblock = np.round_(np.asarray(k)**2/10000) 
    
    try:
        # create directory where to store results
        code, _ = os.path.splitext(os.path.basename(f))
        res_directory = os.path.join('results', code) 
        if os.path.isdir(res_directory): 
            return
        os.mkdir(res_directory)
    

        # pre-process the image
        img_original = read_image(f) 
        img = reshape_image(img_original, int(k[0]*s))
        
        # get horizontal and vertical number of macroblocks
        M = int(np.ceil(img.shape[0]/(k[0]*s)))-1 # horizontal number of macroblocks 
        N = int(np.ceil(img.shape[1]/(k[0]*s)))-1 # vertical number of macroblocks
        
        H_aux = np.zeros((M , N))

        for scale in range(num_scales):
            img_s = extract_scales(img,scale) # define image in the current scale

            io.imsave(f'{res_directory}/{code}_{scale}.png', img_s.astype(np.uint8)) 

            # compute global image noise curve
            bins_global = img_s.shape[0]*img_s.shape[1]/10000
            estim_filename = f"{res_directory}/{code}_{scale}_global.txt"
            ponomarenko(f'{res_directory}/{code}_{scale}.png', estim_filename, b=bins_global, g=g_i) 
            
            # read estimations
            mean_stds_global = {}
            mean_0, mean_1, mean_2, std_0, std_1, std_2 = read_estim(estim_filename)
            mean_stds_global[0] = mean_0, std_0
            mean_stds_global[1] = mean_1, std_1
            mean_stds_global[2] = mean_2, std_2
            
            # compute macroblocks noise curves
            estim_filename = f"{res_directory}/{code}_{scale}_macroblocks.txt"    
            if bins_macroblock[scale]==0: bins_macroblock[scale] =1
            ponomarenko_blocks(f'{res_directory}/{code}_{scale}.png', estim_filename, k[scale], s, b= bins_macroblock[scale], g=g_b)
            
            # read estimations
            mean_mblocks = {}
            std_mblocks = {}
            mean_mblocks[0], mean_mblocks[1], mean_mblocks[2], std_mblocks[0], std_mblocks[1], std_mblocks[2] = read_estim(estim_filename)

            H_s_ch = np.zeros((M,N,3))
            for ch in range(3):
                mus, sigmas = mean_stds_global[ch]
                g = interpolate.interp1d(mus,sigmas)
                for j in range(N):
                    for i in range(M):
                        position0 = int((j+N*i)*bins_macroblock[scale])
                        position1 = int(position0 + bins_macroblock[scale])
                        block_mus, block_sigmas = makeSameXrange(mus, mean_mblocks[ch][position0:position1],std_mblocks[ch][position0:position1])
                        if len(block_mus)>0:
                            H_s_ch[i,j,ch] = 0
                            for m in range(len(block_mus)):
                                if g(block_mus[m])> block_sigmas[m]:
                                    H_s_ch[i,j,ch] = H_s_ch[i,j,ch] +1
                                else: 
                                    H_s_ch[i,j,ch] = H_s_ch[i,j,ch] 
                            H_s_ch[i,j,ch] = H_s_ch[i,j,ch]/len(block_mus)*100
                        else:
                            H_s_ch[i,j,ch] = -100

            H_s = np.zeros((M,N))
            for j in range(N):
                for i in range(M):
                    base = H_s_ch[i,j,0] * H_s_ch[i,j,1] * H_s_ch[i,j,2]
                    H_s[i,j] = base**(1/3) if base > 0 else 0
            H_s /= num_scales*100
            H_s *= 255
            H_aux += H_s
            os.remove(f'{res_directory}/{code}_{scale}.png')
            os.remove(f'{res_directory}/{code}_{scale}_macroblocks.txt' )
            os.remove(f'{res_directory}/{code}_{scale}_global.txt')
            

        H = np.zeros(img_original.shape[0:2], dtype=float)
        for j in range(N):
            for i in range(M):
                H[int(i*s*k[0]): int(i*s*k[0] +k[0]), int(j*s*k[0]): int(j*s*k[0] +k[0])] += H_aux[i,j]/4
        H[0:int(s*k[0]), :] *=2
        H[M*int(s*k[0]): , : ] *=2
        H[:, 0:int(s*k[0])] *=2
        H[:, N*int(s*k[0]): ] *=2

        io.imsave(f'{res_directory}/PB3.png', H.astype(np.uint8), check_contrast=False)

      
    except Exception as ex:
        print(f"Fallo: {f}")
        traceback.print_exc()

    return


# create first level directory
if not os.path.isdir("results"):
    os.mkdir("results")

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.parse_args()
args = parser.parse_args()

f = args.filename
do_one_image(f)

