#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 17:57:53 2019

@author: marina
"""

from skimage import io
import numpy as np
import subprocess

def read_image(filename):
    '''
    Read a three-channel image
    '''
    I = io.imread(filename).astype(np.float)
    
    if len(I.shape) == 2 or I.shape[2] == 1:
        T = np.zeros((I.shape[0], I.shape[1], 3))
        for i in range(3):
            T[:,:,i] = I[:,:]
        I = T.copy()
        
    return I[:, :, :3]

def reshape_image_horizontal(I,k):
    '''
    Symmetrize the borders of the image so its horizontal length is multiple of k
    '''
    missing_pixels_0 = int(k - I.shape[0] % k) 
    I_reshaped = np.zeros((I.shape[0]+ missing_pixels_0, I.shape[1], I.shape[2]))
    for i in range(I.shape[0]+ missing_pixels_0):
        if i < I.shape[0]:
            I_reshaped[i,:,:] = I[i,:,:]
        else:
            dif = i -(I.shape[0] -1)
            I_reshaped[i,:,:] = I[-dif,:,:]
    return I_reshaped

def reshape_image_vertical(I,k):
    '''
    Symmetrize the borders of the image so its vertical length is multiple of k
    '''
    missing_pixels_1 = int(k - I.shape[1] % k) 
    I_reshaped = np.zeros((I.shape[0], I.shape[1]+ missing_pixels_1, I.shape[2]))
    for j in range(I.shape[1]+ missing_pixels_1):
        if j < I.shape[1]:
            I_reshaped[:,j,:] = I[:,j,:]
        else:
            dif = j -(I.shape[1] -1)
            I_reshaped[:,j,:] = I[:,-dif,:]
    return I_reshaped

def reshape_image(I,k):
    '''
    Symmetrize the borders of the image so its horizontal and vertical length is multiple of k
    '''
    return reshape_image_vertical(reshape_image_horizontal(I,k),k)

def ponomarenko(input_filename, output_filename, w=8, p=0.005, b=0, D=7, g=5):
    '''
    Estimate the noise in the input image and store it in a text file
    '''
    line_exec = ('./ponom_src/ponomarenko/ponomarenko', f'-w{w}', f'-p{p}', f'-b{b}', f'-D{D}', f'-g{g}', '-m2', '-r', input_filename) 
    with open(output_filename, "w") as f:
        res = subprocess.run(line_exec, stdout=f)
    assert res.returncode == 0
    
def ponomarenko_blocks(input_filename, output_filename, mblock_size, mblock_stride, w=8, p=0.005, b=0, D=7, g=5):
    '''
    Estimate the noise in the macroblocks of the input image and store it in a text file
    '''
    line_exec = ('./ponom_src/ponomarenko_extract/ponomarenko', f'-a{mblock_size}', f'-o{mblock_stride}' f'-w{w}', f'-p{p}', f'-b{b}', f'-D{D}', f'-g{g}', '-m2', '-r', input_filename)
    with open(output_filename, "w") as f:
        res = subprocess.run(line_exec, stdout=f, stderr=f)
    assert res.returncode == 0
 
def split_estim_3(lines):
    '''
    Read a three-channel estimation file
    '''
    means_r, means_g, means_b = [], [], []
    stds_r, stds_g, stds_b = [], [], []
    
    
    for line in lines:
        r, g, b, std_r, std_g, std_b = line.strip().split('  ')
        r, g, b, std_r, std_g, std_b = float(r), float(g), float(b), float(std_r), float(std_g), float(std_b)
    
        means_r.append(r)
        means_g.append(g)
        means_b.append(b)

        stds_r.append(std_r)
        stds_g.append(std_g)
        stds_b.append(std_b)
    
        
    means_r = np.array(means_r)
    means_g = np.array(means_g)
    means_b = np.array(means_b)
    
    stds_r = np.array(stds_r)
    stds_g = np.array(stds_g)
    stds_b = np.array(stds_b)
    
    return means_r, means_g, means_b, stds_r, stds_g, stds_b 

def split_estim_1(lines):
    '''
    Read a one-channel estimation file
    '''
    means = []
    stds = []

    for line in lines:
        m, s = line.strip().split('  ')
        m, s = float(m), float(s)
    
        means.append(m)
        stds.append(s)
        
    means = np.array(means)
    stds = np.array(stds)
    
    return means, stds 

def read_estim(filename):
    '''
    Read a one or three channel estimation file
    '''
    lines = []
    
    # Read all lines
    with open(filename, "r") as f:
        lines = f.readlines()
        
    # Get number of columns
    num_cols = len(lines[0].strip().split('  '))
    
    if num_cols == 2:
        return split_estim_1(lines)
    elif num_cols == 6:
        return split_estim_3(lines)
    else:
        raise ValueError(f'Bad number of columns: {num_cols}')

def extract_one_scale(I):
    return extract_one_scale_horizontal(extract_one_scale_vertical(I))

def extract_one_scale_horizontal(I):
    M = I.shape[0]
    N = I.shape[1]
    M_s = int(np.floor(M/2))
    I_s = np.zeros((M_s, N, 3))
    for i in range(M_s):
        I_s[i, : , :] = (I[2*i, :, :] + I[2*i+1, :, :])/2
    return I_s

def extract_one_scale_vertical(I):
    M = I.shape[0]
    N = I.shape[1]
    N_s = int(np.floor(N/2))
    I_s = np.zeros((M, N_s, 3))
    for j in range(N_s):
        I_s[:, j , :] = (I[:, 2*j, :] + I[:, 2*j +1, :])/2
    return I_s

def extract_scales(I,n):
    for num_iter in range(n):
        I = extract_one_scale(I)
    return I

def makeSameXrange(theoryX,dataX,dataY):
    '''
    Truncate the dataX and dataY ranges so that dataX min and max are with in
    the max and min of theoryX.
    '''
    minT,maxT = theoryX.min(),theoryX.max()
    goodIdxMax = np.where(dataX<=maxT)
    goodIdxMin = np.where(dataX[goodIdxMax]>=minT)
    return [(dataX[goodIdxMax])[goodIdxMin],(dataY[goodIdxMax])[goodIdxMin]]



