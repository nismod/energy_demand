""" Making of the dictionary --> arrays in a dict called dict_container
    using two nested dictionaries 
"""
import numpy as np
print("ss")
dict_container = {}
sub_dict = {}
subsub_dict = {}

path = "C:/"
files = ['filename_A']

int_time = [1,2,3]

measurement_attribute = ["'ff'"]

corr_factor = 2

sample_list = ["samplename"]

for cnt, file_name in enumerate(files):

    sub_dict = {}
    subsub_dict = {}

    measurement = np.zeros((25))

    subsub_dict[measurement_attribute[cnt]] = measurement * corr_factor 

    sub_dict[int_time[cnt]] = subsub_dict    

    
    dict_container[sample_list[cnt]] = sub_dict
    
    print("----")
    print(sub_dict.keys())

'''from collections import defaultdict(dict)

sub_dict = defaultdict(dict)
main_keys = ['main_A', 'main_B']
sub_kes = ['sub_A', 'sub_B']

for i in main_keys:
    for j in sub_kes:
        sub_dict[i][j] = {}'''



#ein dictionary mit dict_container[sample_name][int_time][measurement_attribute]

#print(dict_container['SY_1']['1s']['initial'])
#print(dict_container['SY_3']['1s']['initial'])
a = {
    'a': {
        'b': {
            'c': 200}}}