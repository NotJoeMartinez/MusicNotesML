
from numpy.core.numeric import full
from mozart_package import *
import glob
import cv2
import pickle
from imutils import resize as im_resize
from scipy.ndimage import binary_fill_holes
from skimage.morphology import skeletonize, thin
from pathlib import Path

import logging
logging.basicConfig(filename="main.log", filemode='w')




def main(args):
    full_img_path = args.img_path
    img_name = Path(full_img_path).stem
    img_ext = Path(full_img_path).suffix 
    # img_pdir = Path(full_img_path).parent

    logging.error(f"full_image_path {full_img_path} {type(full_img_path)}")
    logging.error(f"img_name: {img_name} {type(img_name)}")
    logging.error(f"img_ext: {img_ext} {type(img_ext)}")


    img = io.imread(full_img_path)
    img = gray_img(img)
    show_images([img])
    # img = get_thresholded(img, threshold_otsu(img))
    horizontal = IsHorizontal(img)

    if horizontal == False:
        theta = deskew(img)
        img = rotation(img,theta)
        img = get_gray(img)
        img = get_thresholded(img, threshold_otsu(img))
        img = get_closer(img)
        horizontal = IsHorizontal(img)
    show_images([img])




    original = img.copy()
    gray = get_gray(img)
    bin_img = get_thresholded(gray, threshold_otsu(gray))
    show_images([gray, bin_img], ['Gray', 'Binary'])

    segmenter = Segmenter(bin_img)
    imgs_with_staff = segmenter.regions_with_staff
    imgs_without_staff = segmenter.regions_without_staff

    for i, img in enumerate(imgs_without_staff):
        show_images([img, imgs_with_staff[i]])




    imgs_spacing = []
    imgs_rows = []
    coord_imgs = []
    for i, img in enumerate(imgs_with_staff):
        spacing, rows, no_staff_img = coordinator(img,horizontal)
        imgs_rows.append(rows)
        imgs_spacing.append(spacing)
        coord_imgs.append(no_staff_img)

    def estim(c, idx):
        print('estim idx: ', idx)
        spacing = imgs_spacing[idx]
        rows = imgs_rows[idx]
        margin = 1+(spacing/4)
        for index,line in enumerate (rows):
            if c >= line - margin and c <= line + margin:
                return index+1, 0
            elif c >= line + margin and c <= line + 3*margin:
                return index+1, 1
        return 0 , 0 


    def draw_staff(img,row_positions):
        image = np.copy(img)
        for x in range (len(row_positions)):
            print(int(row_positions[x]))
            image[int(row_positions[x]),:] = 0
        return image

    for i, img in enumerate(coord_imgs):
        new_img = draw_staff(img,imgs_rows[i])
        show_images([img,new_img], ['Binary','new'])  
        cv2.imwrite(f'output/{img_name}_without_staff_{i}.png', np.array(255*img).astype(np.uint8))
        cv2.imwrite(f'output/{img_name}_with_new_staff_{i}.png', np.array(255*new_img).astype(np.uint8))



    black_names = ['4', '8', '8_b_n', '8_b_r', '16', '16_b_n', '16_b_r', '32', '32_b_n', '32_b_r', 'a_4', 'a_8', 'a_16', 'a_32', 'chord']
    ring_names = ['2', 'a_2']
    whole_names = ['1', 'a_1']
    disk_size = segmenter.most_common / 4
    print(len(coord_imgs))
    for i, img in enumerate(coord_imgs):
        show_images([img])
        # notes defined as res on line below
        res = []
        prev = ''
        time_name = ''
        primitives, prim_with_staff, boundary = get_connected_components(img, imgs_with_staff[i])
        print(boundary)  
        # detected is an numpy.ndarray with the size of 977352 idk what that means
        detected = cv2.cvtColor(np.array(255*img.copy()).astype(np.uint8),cv2.COLOR_GRAY2RGB)
        for j, prim in enumerate(primitives):
            minr, minc, maxr, maxc = boundary[j]

            prim = binary_opening(prim, square(segmenter.most_common-imgs_spacing[i]))
            saved_img = (255*(1 - prim)).astype(np.uint8)
            labels = predict(saved_img)
            octave = None
            label = labels[0]

            cv2.rectangle(detected, (minc, minr), (maxc, maxr), (0, 0, 255), 2)
            # cv2.putText(detected, label, (minc-2, minr-2), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            if label in black_names:
                test_img = np.copy(prim_with_staff[j])
                test_img = binary_dilation(test_img, disk(disk_size))
                show_images([prim_with_staff[j], test_img], ['Original', 'Connected Component with staff'])
                comps, comp_w_staff, bounds = get_connected_components(test_img, prim_with_staff[j])
                comps, comp_w_staff, bounds = filter_beams(comps, comp_w_staff, bounds)
                bounds = [np.array(bound)+disk_size-2 for bound in bounds]

                if len(bounds) > 1 and label not in ['8_b_n', '8_b_r', '16_b_n', '16_b_r', '32_b_n', '32_b_r']:
                    l_res = []
                    bounds = sorted(bounds, key= lambda b : -b[2])
                    for k in range(len(bounds)):
                        print("Bound")
                        idx, p = estim(boundary[j][0]+bounds[k][2], i)
                        l_res.append(f'{label_map[idx][p]}/4')
                        if k+1 < len(bounds) and (bounds[k][2]-bounds[k+1][2]) > 1.5*imgs_spacing[i]:
                            print("IF COND", bounds[k][2]-bounds[k+1][2], 1.25*imgs_spacing[i])
                            idx, p = estim(boundary[j][0]+bounds[k][2]-imgs_spacing[i]/2, i)
                            l_res.append(f'{label_map[idx][p]}/4')
                    res.append(sorted(l_res))
                else:
                    for bbox in bounds:
                        c = bbox[2]+boundary[j][0]
                        line_idx, p = estim(int(c), i)
                        l = label_map[line_idx][p]
                        res.append(get_note_name(prev, l, label))
                        print(c)
                        print(l)

            elif label in ring_names:
                head_img = 1-binary_fill_holes(1-prim)
                head_img = binary_closing(head_img, disk(disk_size))
                comps, comp_w_staff, bounds = get_connected_components(head_img, prim_with_staff[j])
                for bbox in bounds:
                    c = bbox[2]+boundary[j][0]
                    line_idx, p = estim(int(c), i)
                    l = label_map[line_idx][p]
                    res.append(get_note_name(prev, l, label))
                    print(c)
                    print(l)

            elif label in whole_names:
                c = boundary[j][2]
                line_idx, p = estim(int(c), i)
                l = label_map[line_idx][p]
                res.append(get_note_name(prev, l, label))
                print(c)
                print(l)

            elif label in ['bar', 'bar_b', 'clef', 'clef_b', 'natural', 'natural_b'] or label in []:
                show_images([prim], [label])
                continue
            elif label in ['#', '#_b']:
                if prim.shape[0] == prim.shape [1]:
                    prev = '##'
                else: 
                    prev = '#'
            elif label in ['cross']:
                prev = '##'
            elif label in ['flat', 'flat_b']:
                if prim.shape[1] >= 0.5*prim.shape[0]:
                    prev = '&&'
                else:
                    prev = '&'
            elif label in ['dot', 'dot_b', 'p', 't24_b']:
                if len(res) == 0 or (len(res) > 0 and res[-1] in ['flat', 'flat_b', 'cross', '#', '#_b', 't24', 't24_b', 't44', 't44_b']):
                    continue
                res[-1] += '.'
            elif label in ['t2', 't4']:
                time_name += label[1]
            elif label in []:
                time_name = label[1]+label[2]
            elif label == 'chord':
                print('Chord')
                img = thin(1-prim.copy(), max_iter=20)
                head_img = binary_closing(1-img, disk(disk_size))
            if label not in ['flat', 'flat_b', 'cross', '#', '#_b']:
                prev = ''
            show_images([prim], [label])
            if len(time_name) == 2:
                res = ["\\" + "meter<\"" + str(time_name[0]) + "/" + str(time_name[1])+"\">"] + res
            
            if len(res) > 0:
                detected_note = res[-1]
                logging.error(f"detected: {detected_note}")
                logging.error(f"detected_note: {detected_note}")
                cv2.putText(detected, detected_note, (minc-2, minr-2), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,225), 2)
            else:
                detected_note = "Unable to detet note"
                # cv2.putText(detected, detected_note, (minc-2, minr-2), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,225), 2)
            

        show_images([detected], ['Detected'])

        no_staff = f'output/{img_name}_detected_{i}.png'
        overlay = f"output/{img_name}_overlay_{i}.png"
        background = full_img_path
        output = f"output/{img_name}_output_{i}.png"

        cv2.imwrite(no_staff, detected)
        import subprocess

        subprocess.run(f"convert {no_staff} -matte \( +clone -fuzz 10% -transparent '#ff0000' \) -compose DstOut -composite {overlay}", shell=True)
        subprocess.run(f"magick composite -colorspace sRGB -gravity center {overlay} {background} {output}", shell=True)
        subprocess.run(f"open {output}", shell=True)









def get_note_name(prev, octave, duration):
    if duration in ['4', 'a_4']:
        return f'{octave[0]}{prev}{octave[1]}/4'
    elif duration in ['8', '8_b_n', '8_b_r', 'a_8']:
        return f'{octave[0]}{prev}{octave[1]}/8'
    elif duration in ['16', '16_b_n', '16_b_r', 'a_16']:
        return f'{octave[0]}{prev}{octave[1]}/16'
    elif duration in ['32', '32_b_n', '32_b_r', 'a_32']:
        return f'{octave[0]}{prev}{octave[1]}/32'
    elif duration in ['2', 'a_2']:
        return f'{octave[0]}{prev}{octave[1]}/2'
    elif duration in ['1', 'a_1']:
        return f'{octave[0]}{prev}{octave[1]}/1'



def filter_beams(prims, prim_with_staff, bounds):
    n_bounds = []
    n_prims = []
    n_prim_with_staff = []
    for i, prim in enumerate(prims):
        if prim.shape[1] >= 2*prim.shape[0]:
            print('filter: ', prim.shape)
            continue
        else:
            n_bounds.append(bounds[i])
            n_prims.append(prims[i])
            n_prim_with_staff.append(prim_with_staff[i])
    return n_prims, n_prim_with_staff, n_bounds




def get_chord_notation(chord_list):
    chord_res = "{"
    for chord_note in chord_list:
        chord_res += (str(chord_note) + ",")
    chord_res = chord_res[:-1]
    chord_res += "}"
    
    return chord_res

if __name__ == '__main__':

    # img_name="08"
    # img_ext = 'png'
    # imgs_path = 'test_imgs/'



    label_map = {
        0:{
            0: 'N0'
        },
        1:{
            0:'b2',
            1:'a2'
        },
        2:{
            0:'g2',
            1:'f2'
        },
        3:{
            0:'e2',
            1:'d2'
        },
        4:{
            0:'c2',
            1:'b1'
        },
        5:{
            0:'a1',
            1:'g1'
        },
        6:{
            0:'f1',
            1:'e1'
        },
        7:{
            0:'d1',
            1:'c1'
        }
    }


    import argparse
    parser = argparse.ArgumentParser(description='Overlays finger numbers')
    parser.add_argument('-p','--img-path', type=str, help='the path to original image')
    args = parser.parse_args()
    main(args)