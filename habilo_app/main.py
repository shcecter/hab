import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import click


@click.command()
@click.option('--filename', prompt='type file name')
def render_figures(filename):
    filename = '../data/' + filename
    filename += '.csv'
    plot_data(filename)
    plt.show()


'''
Функции для считывания и преобразования исходных данных
'''


def read_data(filename):
    data = pd.read_csv(filename, sep=';', decimal='.')
    return data


def get_angle(top_tup, mid_tup, bottom_tup):
    top_seg_tup = (top_tup[0] - mid_tup[0], top_tup[1] - mid_tup[1])
    bottom_seg_tup = (mid_tup[0] - bottom_tup[0], mid_tup[1] - bottom_tup[1])

    angle_from_atan2 = np.arctan2(top_seg_tup[0], top_seg_tup[1]) - np.arctan2(bottom_seg_tup[0], bottom_seg_tup[1])
    return np.rad2deg(angle_from_atan2)


def loc_constructor(side, seg, axis):
    if seg != 'Spine':
        loc_name = seg + side + '_' + axis + ' [cm]'
    else:
        loc_name = seg + '_' + axis + ' [cm]'
    return loc_name


def get_joint(data, segs_l, side):
    names_l_x = [loc_constructor(side, seg, 'Y') for seg in segs_l]
    names_l_y = [loc_constructor(side, seg, 'Z') for seg in segs_l]
    vecs_l_ax = [data[name].values for name in names_l_x]
    vecs_l_ay = [data[name].values for name in names_l_y]
    to_get_angle_l = [[x, y] for x, y in zip(vecs_l_ax, vecs_l_ay)]
    joint = get_angle(*(to_get_angle_l))
    return joint


def get_joints(data, segs_l):
    sides_t = ('Left', 'Right')
    joints_l = []
    for side in sides_t:
        joints_l.append(get_joint(data, segs_l, side))

    return joints_l


def get_time(data):
    time = data['Time [sec]']
    return time.values


def create_curves(data):
    hip_segs_l = ['Spine', 'Hip', 'Knee']
    knee_segs_l = ['Hip', 'Knee', 'Ankle']
    time = get_time(data)
    hip = get_joints(data, hip_segs_l)
    knee = get_joints(data, knee_segs_l)
    spine_z = data['Spine_Y [cm]'].values
    return {'time': time, 'hip': hip, 'knee': knee, 'spine': spine_z}


'''
Функции для редактирования исходных данных
'''


def get_nearest(arr, value):
    """
    Returns: index of value in array that is nearest to value
    """
    difference_arr = np.abs(arr - value)
    idx = np.argmin(difference_arr)
    return idx


def cut_data(data, first=0, last=None):
    '''
    Функция для обрезания данных по значениям амплитуд
    '''
    time = get_time(data)
    if last is None:
        last = len(time)
    i = get_nearest(time, first)
    k = get_nearest(time, last)
    return data[i:k]


def cut_outpoint(filename):
    '''
    under heavy development
    '''
    data = read_data(filename)
    pass


'''
Подготовка графиков
'''


def get_plot_size(num_timesteps):
    width = num_timesteps / 35
    return width


def plot_data(filename, spine_z_f=False, phase_f=True, autoout=True):
    data = read_data(filename)
    curves = create_curves(data)
    time = curves['time']
    hip = curves['hip']
    knee = curves['knee']
    spine_z = curves['spine']
    lhip, rhip = hip
    lknee, rknee = knee
    if autoout:
        if lknee.max() > 60 or rknee > 60:
            lidx = get_nearest(lknee, 60)
            ridx = get_nearest(rknee, 60)
            earl = lidx if lidx < ridx else ridx
            cutted_data = data[0:earl]
            curves = create_curves(cutted_data)
            time = curves['time']
            hip = curves['hip']
            knee = curves['knee']
            spine_z = curves['spine']
            lhip, rhip = hip
            lknee, rknee = knee
            click.echo('Here goes with cutting outlying points....')
        else:
            click.echo('there is nothing to cut! No outlying points in this data.')
    if spine_z_f:
        fig, (ahip, aknee, aspine) = plt.subplots(3, 1)
        fig.set_size_inches(get_plot_size(time.shape[0]), 6)
        ahip.plot(time, lhip)
        ahip.plot(time, rhip)
        ahip.set_ylim(-50, 30)
        ahip.set_title('Hip')
        aknee.plot(time, lknee)
        aknee.plot(time, rknee)
        aknee.set_ylim(-10, 60)
        aknee.set_title('Knee')
        aspine.plot(time, spine_z)
        aspine.set_title('Spine center height')
    else:
        fig, (ahip, aknee) = plt.subplots(2, 1)
        fig.set_size_inches(get_plot_size(time.shape[0]), 6)
        ahip.plot(time, lhip, '-', label='left')
        ahip.plot(time, rhip, label='right')
        ahip.set_ylim(-50, 30)
        ahip.set_title('Hip')
        ahip.legend()
        aknee.plot(time, lknee, '-', label='left')
        aknee.plot(time, rknee, label='right')
        aknee.set_ylim(-10, 60)
        aknee.set_title('Knee')
        aknee.legend()
        fig.suptitle('Гониометрия коленного и тазобедренного суставов')
    if phase_f:
        plt.figure()
        plt.plot(lknee, lhip, 'b', label='left')
        plt.plot(rknee, rhip, 'r', label='right')
        plt.legend()


if __name__ == '__main__':
    render_figures()
