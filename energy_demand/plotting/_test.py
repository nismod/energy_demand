import math
import matplotlib.pyplot as plt

# Some data
fracs = [15, 30, 45, 10]

# Make figure and axes
fig, axs = plt.subplots(2,2)



standard_area_to_define_radius = 4

old_area = 1
new_area = 2

area_change = new_area / old_area

old_radius = (1 / standard_area_to_define_radius) * old_area

#new_radius = math.sqrt(area_change * new_area / math.pi)
new_radius = math.sqrt(area_change) * old_radius

axs[1,0].pie(fracs, radius=old_radius)
axs[1,1].pie(fracs, radius=new_radius)

plt.show()