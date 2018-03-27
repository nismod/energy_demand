"""
Create dynamic gif file from results

VALID_EXTENSIONS = ('png', 'jpg')

http://www.idiotinside.com/2017/06/06/create-gif-animation-with-python/

"""
import os
import datetime
import imageio

def create_gif(filenames, duration, path):
    """
    """
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    output_file_name = 'Gif-%s.gif' % datetime.datetime.now().strftime('%Y-%M-%d-%H-%M-%S')
    output_file = os.path.join(path, output_file_name)
    imageio.mimsave(output_file, images, duration=duration)


'''if __name__ == "__main__":
    script = sys.argv.pop(0)

    if len(sys.argv) < 2:
        print('Usage: python {} <duration> <path to images separated by space>'.format(script))
        sys.exit(1)

    duration = float(sys.argv.pop(0))
    filenames = sys.argv


    if not all(f.lower().endswith(VALID_EXTENSIONS) for f in filenames):
        print('Only png and jpg files allowed')
        sys.exit(1)

    create_gif(filenames, duration)'''


def get_all_results(path_to_scenario, file_name_part):

    
    scenario_results = os.path.join(path_to_scenario, '_result_data', 'spatial_results')

    # Iterate all files
    result_files = os.listdir(scenario_results)

    filenames = []

    for file_name in result_files:

        try:
            print(file_name.split(file_name_part))
            if len(file_name.split(file_name_part)) == 2:
                filenames.append(os.path.join(scenario_results, file_name))
        except:
            pass
    
    create_gif(filenames, duration=1, path=scenario_results)
    print("finished creating gif")

#get_all_results(r"C:\Users\cenv0553\nismod\data_energy_demand\_MULT2\ase", 'lf_diff')