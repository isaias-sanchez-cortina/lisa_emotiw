# Copyright (c) 2013 University of Montreal, Hani Almousli, Pascal Vincent
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * The names of the authors and contributors to this software may not be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import scipy.io

from faceimages import FaceImagesDataset

def avg_2(a, b):
    return ((a[0] + b[0])/2, (a[1] + b[1])/2)

class MultiPie(FaceImagesDataset):
    """The CMU Multi-PIE Face Database"""
    
    def __init__(self):
        super(MultiPie,self).__init__("MultiPie", "faces/Multi-Pie/")
        self.lstImages= []
        self.lstgender=[]
                             
        label = self.absolute_base_directory+'MPie_Labels/labels/'

        #read male and female
        metaPath = self.absolute_base_directory+'meta/subject_list.txt'
        f = open(metaPath)
        f_lines = f.readlines()
        self.num_subjects = len(f_lines)

        i = 0
        self.subject_id_to_idx = {}

        for line in f_lines:
            if line!='':
                self.lstgender.append(line.split(' ')[2])
                self.subject_id_to_idx[line.split(' ')[0]] = i
                i += 1
        
        cam = os.listdir(label)
        for c in cam:
            files = os.listdir(label+c)
            files.sort()
            for f in files:
                # imrelpath=self.absolute_base_directory+'data/'
                imrelpath='data/'
                parts = f.split('.')[0].split('_')
                subject = int(parts[0])
                session= parts[1]
                rec_num = parts[2]
                imrelpath += 'session'+session+'/multiview/'+parts[0]+'/'+rec_num+'/'+parts[3][0]+parts[3][1]+"_"+parts[3][2]+'/'
                imrelpath += "_".join(parts[0:5])+'.png'
                filename = label+c+'/'+f
                #print "loading ", filename #printing is slow and lots of files are being loaded.
                pts_idx_dict_68 = {0: 'right_ear_top', 1: 'right_ear_center', 2: 'right_ear_bottom', 3: 'right_cheek_0', 4: 'right_cheek_1', 5: 'right_jaw_0', 6: 'right_jaw_1', 7: 'chin_right', 8: 'chin_center', 9: 'chin_left', 10: 'left_jaw_1', 11: 'left_jaw_0', 12: 'left_cheek_1', 13: 'left_cheek_0', 14: 'left_ear_bottom', 15: 'left_ear_center', 16: 'left_ear_top', 17: 'right_eyebrow_outer_end', 18: 'right_eyebrow_outer_midpoint', 19: 'right_eyebrow_center', 20: 'right_eyebrow_inner_midpoint', 21: 'right_eyebrow_inner_end', 22: 'left_eyebrow_inner_end', 23: 'left_eyebrow_inner_midpoint', 24: 'left_eyebrow_center', 25: 'left_eyebrow_outer_midpoint', 26: 'left_eyebrow_outer_end', 27: 'nose_center_top', 28: 'nose_ridge_top', 29: 'nose_ridge_bottom', 30: 'nose_tip', 31: 'right_nostril', 32: 'right_nostril_inner_end', 33: 'nostrils_center', 34: 'left_nostril_inner_end', 35: 'left_nostril', 36: 'right_eye_outer_corner', 37: 'right_eye_top_outer_midpoint', 38: 'right_eye_top_inner_midpoint', 39: 'right_eye_inner_corner', 40: 'right_eye_bottom_inner_midpoint', 41: 'right_eye_bottom_outer_midpoint', 42: 'left_eye_inner_corner', 43: 'left_eye_top_inner_midpoint', 44: 'left_eye_top_outer_midpoint', 45: 'left_eye_outer_corner', 46: 'left_eye_bottom_outer_midpoint', 47: 'left_eye_bottom_inner_midpoint', 48: 'mouth_right_corner', 49: 'top_lip_top_right_midpoint', 50: 'top_lip_top_right_center', 51: 'mouth_top_lip', 52: 'top_lip_top_left_center', 53: 'top_lip_top_left_midpoint', 54: 'mouth_left_corner', 55: 'bottom_lip_bottom_left_midpoint', 56: 'bottom_lip_bottom_left_center', 57: 'mouth_bottom_lip', 58: 'bottom_lip_bottom_right_center', 59: 'bottom_lip_bottom_right_midpoint', 60: 'top_lip_bottom_right_midpoint', 61: 'top_lip_bottom_right_center', 62: 'top_lip_bottom_center', 63: 'top_lip_bottom_left_center', 64: 'bottom_lip_top_left_midpoint', 65: 'bottom_lip_top_left_center', 66: 'bottom_lip_top_center', 67: 'bottom_lip_top_right_center'}

                pts_idx_dict_39 = {0: 'nose_center_top', 1: 'nose_ridge_top', 2: 'nose_ridge_bottom', 3: 'nose_tip', 4: 'nostrils_center', 5: 'left_nostril', 6: 'left_eyebrow_outer_end', 7: 'left_eyebrow_outer_midpoint', 8: 'left_eyebrow_inner_midpoint', 9: 'left_eyebrow_inner_end', 10: 'left_eye_outer_corner', 11: 'left_eye_top_outer_midpoint', 12: 'left_eye_top_inner_midpoint', 13: 'left_eye_bottom_outer_midpoint', 14: 'left_eye_bottom_inner_midpoint', 15: 'mouth_top_lip', 16: 'top_lip_top_left_center', 17: 'top_lip_top_left_midpoint', 18: 'mouth_left_corner', 19: 'bottom_lip_bottom_left_midpoint', 20: 'bottom_lip_bottom_left_center', 21: 'mouth_bottom_lip', 22: 'bottom_lip_top_center', 23: 'top_lip_bottom_left_center', 24: 'top_lip_bottom_left_midpoint', 25: 'bottom_lip_top_left_midpoint', 26: 'bottom_lip_top_left_center', 27: 'mouth_bottom_lip', 28: 'chin_center_top', 29: 'chin_center', 30: 'left_jaw_2', 31: 'left_jaw_1', 32: 'left_jaw_0', 33: 'left_cheek_2', 34: 'left_cheek_1', 35: 'left_cheek_0', 36: 'left_ear_bottom', 37: 'left_ear_center', 38: 'left_ear_top'}

                points = scipy.io.loadmat(filename)['pts']
                this_dict = {}
                translation_dict = pts_idx_dict_68
    
                if len(points) == 39:
                    translation_dict = pts_idx_dict_39

                for idx, p in enumerate(points):
                    if idx in translation_dict:
                        name = translation_dict[idx]

                        if '/01_0/' in imrelpath or '/24_0/' in imrelpath:
                            name = name.replace('left', 'right') #The points for left-facing and
                                                                 #right-facing cameras are symmetric!
                    else:
                        name = 'point_' + str(idx)
                    
                    this_dict[name] = (p[0], p[1])

                emotion = None
                sess_int = int(session)
                rec_int = int(rec_num) 

                if sess_int == 1:
                    if rec_int == 1:
                        emotion = 'neutral'
                    else:
                        emotion = 'happy'
                elif sess_int == 2:
                    if rec_int == 1:
                        emotion = 'neutral'
                    elif rec_int == 2:
                        emotion = 'surprise'
                    else:
                        emotion = 'neutral' #squinting

                elif sess_int == 3:
                    if rec_int == 1:
                        emotion = 'neutral'
                    elif rec_int == 2:
                        emotion = 'happy'
                    else:
                        emotion = 'disgust'

                else:
                    if rec_int == 1 or rec_int == 3:
                        emotion = 'neutral'
                    else:
                        emotion = 'fear' #actually "scream"

                #There are some subjects without male or female information                
                if subject<len(self.lstgender):
                    self.lstImages.append([imrelpath,subject,this_dict,self.lstgender[subject],emotion])
                else:
                    self.lstImages.append([imrelpath,subject,this_dict,"",emotion])

    def get_7emotion_index(self, i):
        #from TFD
        emotionsDic = { "anger":0, "disgust":1, "fear":2 , "happy":3, "sadness":4, "surprise":5, "neutral":6, "contempt":7}
        idx = emotionsDic[self.lstImages[i][4]]
        if idx==7:
            return 0 # contempt is not one of those considered in the definition of this method in the base class, we map it to anger
        return idx
    
    def __len__(self):
        return len(self.lstImages)        
        
    def get_original_image_path_relative_to_base_directory(self, i):       
        return self.lstImages[i][0]    
    
    def get_eyes_location(self, i):
        """
        returns the eye on the left in the image (assumed to be the right eye),
        and then the rigth-most eye (assumed to be the left eye).        
        The eye center is calculated from the average of the top and bottom for each eye,
        which itself is calculated from the average of the points left or right of those
        top or bottom centers (37, 38; 40, 41 for the right eye and 43, 44; 46, 47 for the left eye).
        As for side cameras, the eye center becomes the average of points (11, 12; 13, 14) for whichever
        eye is available.
        """
        if(len(self.lstImages[i][2]) == 39):
            eye_num = -1
            try:
                try: 
                    self.lstImages[i][2]['right_eye_outer_corner']
                    eye_num = 0
                except KeyError:
                    eye_num = 1
            finally:
                try:
                    eye = avg_2(avg_2(self.lstImages[i][2]['point_11'], self.lstImages[i][2]['point_12']),
                                avg_2(self.lstImages[i][2]['point_13'], self.lstImages[i][2]['point_14']))
                    if eye_num == 0:
                        return list(eye + (None, None))
                    else:
                        return list((None, None) + eye)
                except KeyError:
                    return list((None, None, None, None))
        else:
            try:
                try:
                    righteye = avg_2(avg_2(self.lstImages[i][2]['point_37'], self.lstImages[i][2]['point_38']),
                                avg_2(self.lstImages[i][2]['point_40'], self.lstImages[i][2]['point_41']))
                except KeyError:
                    righteye = (None, None)

            finally:
                try:
                    try:
                        lefteye = avg_2(avg_2(self.lstImages[i][2]['point_43'], self.lstImages[i][2]['point_44']),
                            avg_2(self.lstImages[i][2]['point_46'], self.lstImages[i][2]['point_47']))
                    except KeyError:
                        lefteye = (None, None)
                finally:
                    return [righteye[0], righteye[1], lefteye[0], lefteye[1]]
    
    def get_keypoints_location(self,i):
        """
        Check MPie_Labels/examples/ to see which corresponds to what
        """        
        return [self.lstImages[i][2]]    
        
    def get_subject_id_of_ith_face(self, i):
        return self.subject_id_to_idx[self.lstImages[i][1]]
        
    def get_id_of_kth_subject(self, k):    
        for x in self.subject_id_to_idx:
            if self.subject_id_to_idx[x] == k:
                return x
        return -1
        
    def get_gender(self,i):        
        return str(self.lstImages[i][3])

    def get_n_subjects(self):
        return self.num_subjects
            
def testWorks():
    save = 0
    import pickle
    if (save):
        obj = MultiPie()
        output = open('multipie.pkl', 'wb')
        data = obj
        pickle.dump(data, output)
        output.close()
    else:
        pkl_file = open('multipie.pkl', 'rb')
        obj = pickle.load(pkl_file)
        pkl_file.close()

    obj.verify_samples()

if __name__ == '__main__':
    testWorks()
