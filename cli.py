from mozart.commonfunctions import *
from mozart.pre_processing import *
from mozart.connected_componentes import *
from mozart.show_overlayed_plots import show_og_overlayed
from mozart.staff import calculate_thickness_spacing, remove_staff_lines, coordinator
from mozart.segmenter import Segmenter
from mozart.fit import predict
from glob import glob
import cv2
import pickle
from scipy.ndimage import binary_fill_holes
from skimage.morphology import thin
import argparse

from mozart.label_map import get_label_map
label_map = get_label_map()

def estim(c, idx, imgs_spacing, imgs_rows):
    spacing = imgs_spacing[idx]
    rows = imgs_rows[idx]
    margin = 1+(spacing/4)
    for index, line in enumerate(rows):
        if c >= line - margin and c <= line + margin:
            return index+1, 0
        elif c >= line + margin and c <= line + 3*margin:
            return index+1, 1
    return 7, 1


def get_note_name(prev, octave, duration, fnum="True", instrament="trumpet"):
    from mozart.note_dict import note_dict
    try:
        note_name = f'{octave[0]}{prev}{octave[1]}'
    except:
        note_name = "NaN"
        pass
    try:
        finger_num = note_dict[note_name.upper()][instrament]
    except:
        finger_num = "NaN" 
        pass

    if fnum=="True":
        if duration in ['4', 'a_4']:
            return f'{note_name}/{finger_num}'

        elif duration in ['8', '8_b_n', '8_b_r', 'a_8']:
            return f'{note_name}/{finger_num}'

        elif duration in ['16', '16_b_n', '16_b_r', 'a_16']:
            return f'{note_name}/{finger_num}'

        elif duration in ['32', '32_b_n', '32_b_r', 'a_32']:
            return f'{note_name}/{finger_num}'

        elif duration in ['2', 'a_2']:
            return f'{note_name}/{finger_num}'

        elif duration in ['1', 'a_1']:
            return f'{note_name}/{finger_num}'
        else:
            note_name = 'c1'
            try:
                finger_num = note_dict[note_name.upper()] 
            except:
                finger_num = "NaN"
                
            return f"{note_name}/{finger_num}"



    # if duration in ['4', 'a_4']:
    #     return f'{octave[0]}{prev}{octave[1]}/4'
    # elif duration in ['8', '8_b_n', '8_b_r', 'a_8']:
    #     return f'{octave[0]}{prev}{octave[1]}/8'
    # elif duration in ['16', '16_b_n', '16_b_r', 'a_16']:
    #     return f'{octave[0]}{prev}{octave[1]}/16'
    # elif duration in ['32', '32_b_n', '32_b_r', 'a_32']:
    #     return f'{octave[0]}{prev}{octave[1]}/32'
    # elif duration in ['2', 'a_2']:
    #     return f'{octave[0]}{prev}{octave[1]}/2'
    # elif duration in ['1', 'a_1']:
    #     return f'{octave[0]}{prev}{octave[1]}/1'
    # else:
    #     return "c1/4"

def get_only_note_name(prev, octave, duration):
    if duration in ['4', 'a_4']:
        return f'{octave[0]}{prev}{octave[1]}'
    elif duration in ['8', '8_b_n', '8_b_r', 'a_8']:
        return f'{octave[0]}{prev}{octave[1]}'
    elif duration in ['16', '16_b_n', '16_b_r', 'a_16']:
        return f'{octave[0]}{prev}{octave[1]}'
    elif duration in ['32', '32_b_n', '32_b_r', 'a_32']:
        return f'{octave[0]}{prev}{octave[1]}'
    elif duration in ['2', 'a_2']:
        return f'{octave[0]}{prev}{octave[1]}'
    elif duration in ['1', 'a_1']:
        return f'{octave[0]}{prev}{octave[1]}'
    else:
        return "c1"

def filter_beams(prims, prim_with_staff, bounds):
    n_bounds = []
    n_prims = []
    n_prim_with_staff = []
    for i, prim in enumerate(prims):
        if prim.shape[1] >= 2*prim.shape[0]:
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


def draw_staff(img,row_positions):
    image = np.copy(img)
    for x in range (len(row_positions)):
        print(int(row_positions[x]))
        image[int(row_positions[x]),:] = 0
    return image

def recognize(out_file, img_name, full_img_path, most_common, coord_imgs, imgs_with_staff, imgs_spacing, imgs_rows, instrament):
    black_names = ['4', '8', '8_b_n', '8_b_r', '16', '16_b_n', '16_b_r',
                   '32', '32_b_n', '32_b_r', 'a_4', 'a_8', 'a_16', 'a_32', 'chord']
    ring_names = ['2', 'a_2']
    whole_names = ['1', 'a_1']
    disk_size = most_common / 4
    if len(coord_imgs) > 1:
        out_file.write("{\n")
    for i, img in enumerate(coord_imgs):
        res = []
        prev = ''
        time_name = ''
        primitives, prim_with_staff, boundary = get_connected_components(
            img, imgs_with_staff[i])


        # for drawing box
        detected = cv2.cvtColor(np.array(255*img.copy()).astype(np.uint8),cv2.COLOR_GRAY2RGB)
        for j, prim in enumerate(primitives):
            # for drawing box
            minr, minc, maxr, maxc = boundary[j]

            prim = binary_opening(prim, square(
                np.abs(most_common-imgs_spacing[i])))
            saved_img = (255*(1 - prim)).astype(np.uint8)
            labels = predict(saved_img)
            octave = None
            label = labels[0]

            # for drawing box
            # cv2.rectangle(detected, (minc, minr), (maxc, maxr), (0, 0, 255), 2)

            if label in black_names:
                test_img = np.copy(prim_with_staff[j])
                test_img = binary_dilation(test_img, disk(disk_size))
                comps, comp_w_staff, bounds = get_connected_components(
                    test_img, prim_with_staff[j])
                comps, comp_w_staff, bounds = filter_beams(
                    comps, comp_w_staff, bounds)
                bounds = [np.array(bound)+disk_size-2 for bound in bounds]

                if len(bounds) > 1 and label not in ['8_b_n', '8_b_r', '16_b_n', '16_b_r', '32_b_n', '32_b_r']:
                    l_res = []
                    bounds = sorted(bounds, key=lambda b: -b[2])
                    for k in range(len(bounds)):
                        idx, p = estim(
                            boundary[j][0]+bounds[k][2], i, imgs_spacing, imgs_rows)
                        l_res.append(f'{label_map[idx][p]}/4')
                        if k+1 < len(bounds) and (bounds[k][2]-bounds[k+1][2]) > 1.5*imgs_spacing[i]:
                            idx, p = estim(
                                boundary[j][0]+bounds[k][2]-imgs_spacing[i]/2, i, imgs_spacing, imgs_rows)
                            l_res.append(f'{label_map[idx][p]}/4')
                    res.append(sorted(l_res))
                else:
                    for bbox in bounds:
                        c = bbox[2]+boundary[j][0]
                        line_idx, p = estim(int(c), i, imgs_spacing, imgs_rows)
                        l = label_map[line_idx][p]
                        res.append(get_note_name(prev, l, label, fnum="True", instrament=instrament))
            elif label in ring_names:
                head_img = 1-binary_fill_holes(1-prim)
                head_img = binary_closing(head_img, disk(disk_size))
                comps, comp_w_staff, bounds = get_connected_components(
                    head_img, prim_with_staff[j])
                for bbox in bounds:
                    c = bbox[2]+boundary[j][0]
                    line_idx, p = estim(int(c), i, imgs_spacing, imgs_rows)
                    l = label_map[line_idx][p]
                    res.append(get_note_name(prev, l, label, fnum="True", instrament=instrament))
            elif label in whole_names:
                c = boundary[j][2]
                line_idx, p = estim(int(c), i, imgs_spacing, imgs_rows)
                l = label_map[line_idx][p]
                res.append(get_note_name(prev, l, label))
            elif label in ['bar', 'bar_b', 'clef', 'clef_b', 'natural', 'natural_b', 't24', 't24_b', 't44', 't44_b'] or label in []:
                continue
            elif label in ['#', '#_b']:
                if prim.shape[0] == prim.shape[1]:
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
            elif label in ['dot', 'dot_b', 'p']:
                if len(res) == 0 or (len(res) > 0 and res[-1] in ['flat', 'flat_b', 'cross', '#', '#_b', 't24', 't24_b', 't44', 't44_b']):
                    continue
                res[-1] += '.'
            elif label in ['t2', 't4']:
                time_name += label[1]
            elif label == 'chord':
                img = thin(1-prim.copy(), max_iter=20)
                head_img = binary_closing(1-img, disk(disk_size))
            if label not in ['flat', 'flat_b', 'cross', '#', '#_b']:
                prev = ''

            # puts notes on images 
            if len(res) > 0:
                detected_notes = res[-1]
                # check for multiple notes
                if len(detected_notes)>1:
                    notes_str = ""
                    for note in detected_notes:
                        notes_str += note
                    cv2.putText(detected, notes_str, (minc-2, minr-2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                else:
                    cv2.putText(detected, detected_notes, (minc-2, minr-2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
            else:
                detected_note = "Unable to detect note"            

        if len(time_name) == 2:
            notes = "[ " + "\\" + "meter<\"" + str(time_name[0]) + "/" + str(time_name[1])+"\">" + ' '.join(
                [str(elem) if type(elem) != list else get_chord_notation(elem) for elem in res]) + "]\n"
            out_file.write(notes)

        elif len(time_name) == 1:
            notes = "[ " + "\\" + "meter<\"" + '4' + "/" + '2' + "\">" + ' '.join(
                [str(elem) if type(elem) != list else get_chord_notation(elem) for elem in res]) + "]\n"
            out_file.write(notes)
        else:
            notes = "[ " + ' '.join(
                [str(elem) if type(elem) != list else get_chord_notation(elem) for elem in res]) + "]\n"
            out_file.write(notes)




    if len(coord_imgs) > 1:
        out_file.write("}")

    no_staff = f'testing/testing_output/nostaff_detected_{i}.png'
    overlay = f"testing/testing_output/{img_name}_overlay_{i}.png"
    background = f"testing/testing_imgs/{img_name}.png"
    output = f"testing/testing_output/output_{img_name}.png"

    cv2.imwrite(no_staff, detected)

    import subprocess
    subprocess.run(f"convert {no_staff} -matte \( +clone -fuzz 10% -transparent '#ff0000' \) -compose DstOut -composite {overlay}", shell=True)
    subprocess.run(f"magick composite -colorspace sRGB -gravity center {overlay} {background} {output}", shell=True)
    show_og_overlayed(full_img_path, output, res)

    print("###########################", res, "##########################")



def main(args):
    if args.read_fingernums:
        import pandas as pd
        df = pd.read_csv("testing/FingeringTable.csv")
        print(df)

    elif args.file:
        instrament = args.instrament
        print(instrament)
        img_path = args.file
        img_name = img_path.split('/')[-1].split('.')[0]
        output_path = "testing/testing_output"
        out_file = open(f'{output_path}/{img_name}.txt', "w")
        full_img_path = img_path
        print(f"Processing new image {img_name}...")
        img = io.imread(img_path)
        img = gray_img(img)
        horizontal = IsHorizontal(img)

        if horizontal == False:
            theta = deskew(img)
            img = rotation(img, theta)
            img = get_gray(img)
            img = get_thresholded(img, threshold_otsu(img))
            img = get_closer(img)
            horizontal = IsHorizontal(img)

        original = img.copy()
        gray = get_gray(img)
        bin_img = get_thresholded(gray, threshold_otsu(gray))        
        segmenter = Segmenter(bin_img)
        imgs_with_staff = segmenter.regions_with_staff
        most_common = segmenter.most_common
        imgs_spacing = []
        imgs_rows = []
        coord_imgs = []
        for i, img in enumerate(imgs_with_staff):
            spacing, rows, no_staff_img = coordinator(img, horizontal)
            imgs_rows.append(rows)
            imgs_spacing.append(spacing)
            coord_imgs.append(no_staff_img)

        print("Recognize...")
        recognize(out_file, img_name, full_img_path, most_common, coord_imgs,
                imgs_with_staff, imgs_spacing, imgs_rows, instrament)
        out_file.close()
        print("Done...")


    elif args.input_dir != "" and args.output_dir != "":
        instrament = args.instrament
        input_path = args.input_dir 
        output_path = args.output_dir
        img_paths = sorted(glob(f'{input_path}/*'))
        for img_path in img_paths:
            img_name = img_path.split('/')[-1].split('.')[0]
            out_file = open(f'{output_path}/{img_name}.txt', "w")
            full_img_path = img_path
            print(f"Processing new image {img_name}...")
            img = io.imread(img_path)
            img = gray_img(img)
            horizontal = IsHorizontal(img)
            if horizontal == False:
                theta = deskew(img)
                img = rotation(img, theta)
                img = get_gray(img)
                img = get_thresholded(img, threshold_otsu(img))
                img = get_closer(img)
                horizontal = IsHorizontal(img)

            original = img.copy()
            gray = get_gray(img)
            bin_img = get_thresholded(gray, threshold_otsu(gray))

            segmenter = Segmenter(bin_img)
            imgs_with_staff = segmenter.regions_with_staff
            most_common = segmenter.most_common

            # imgs_without_staff = segmenter.regions_without_staff

            imgs_spacing = []
            imgs_rows = []
            coord_imgs = []
            for i, img in enumerate(imgs_with_staff):
                spacing, rows, no_staff_img = coordinator(img, horizontal)
                imgs_rows.append(rows)
                imgs_spacing.append(spacing)
                coord_imgs.append(no_staff_img)

            print("Recognize...")
            recognize(out_file, img_name, full_img_path, most_common, coord_imgs,
                    imgs_with_staff, imgs_spacing, imgs_rows, instrament)
            out_file.close()
            print("Done...")




if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file", action="store", help="test one file")
    parser.add_argument("-i","--input-dir", help="Input directory")
    parser.add_argument("-o","--output-dir", help="Output directory")
    parser.add_argument("-fn", "--read-fingernums", action='store_true', help="read finger num stuff")
    parser.add_argument("-is", "--instrament", action="store", help="Specifed instrament")

    args = parser.parse_args()
    main(args)
